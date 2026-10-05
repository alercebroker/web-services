# catshtm chart

Helm chart for the catsHTM crossmatch API (`catshtm.alerce.online` and `api.alerce.online/catshtm/v1`).
The multisurvey and ZTF crossmatch APIs both call it.

| | |
|---|---|
| Helm release | `ws-catshtm-old`, in Helm namespace `default` |
| Kubernetes namespace / Deployment | `ws-catshtm-old` / `catshtm-api` |
| Values | SSM parameter `/ws-legacy/catshtm-old-helm-values` (production account, `us-east-1`) |
| Catalog data | EBS volume, 1850 GiB, `us-east-1a`, mounted by the app at `/usr/local/catalogsHTM` |

Until 10/2026 this chart existed only inside the Helm release. It was extracted from release revision 19,
checked to re-render the live manifests byte for byte, and then gained the optional `strategyType` value
(chart 0.1.1, deployed as revision 21).

## Deploy

Same rules as the other APIs (see [`multisurveys-apis/DEPLOYMENT.md`](../../multisurveys-apis/DEPLOYMENT.md)):
change the values in SSM, review with `helm diff`, then `helm upgrade` from exactly what SSM holds. Don't
change the live Deployment with `kubectl`.

```bash
export AWS_PROFILE=<your production profile> AWS_REGION=us-east-1
P=/ws-legacy/catshtm-old-helm-values
umask 077; f=$(mktemp --suffix=.yaml)          # the values include sensitive data
aws ssm get-parameter --name $P --output json | jq -j .Parameter.Value > $f
# edit $f, then:
helm diff upgrade ws-catshtm-old charts/catshtm -n default -f $f --three-way-merge
aws ssm put-parameter --name $P --value file://$f --overwrite
cmp <(aws ssm get-parameter --name $P --output json | jq -j .Parameter.Value) $f   # no output = identical
helm upgrade ws-catshtm-old charts/catshtm -n default \
  -f <(aws ssm get-parameter --name $P --output json | jq -j .Parameter.Value)
kubectl rollout status deploy/catshtm-api -n ws-catshtm-old
rm -f $f
```

Use `--output json | jq -j`, not `--output text`: the text output adds a trailing newline, so the
read-back never matches byte for byte.

## Things to know

- **One pod, one disk.** The catalogs sit on a ReadWriteOnce EBS volume, which attaches to one node at a
  time. The values set `strategyType: Recreate`, so an upgrade stops the old pod before starting the new
  one, with about 1–2 minutes of downtime. With the default rolling update, the new pod can land on
  another node and wait forever for the volume. Deleting the old pod doesn't help: its ReplicaSet
  recreates it, and the replacement can grab the volume first.
- **Memory.** The single gunicorn worker keeps every catalog's index file in memory (about 470 MiB), and
  heavy cone searches load whole catalog tiles. The limit was raised from 2 GiB to 3 GiB in 10/2026 after
  about 20 out-of-memory kills per day. Adding gunicorn workers multiplies the index memory, so raise the
  limit with them.
- **Check SSM against the live release before deploying.** The SSM copy was once missing the `resources`
  block that had been applied to the release directly. Compare `helm get values ws-catshtm-old -n default`
  with SSM before you edit.
