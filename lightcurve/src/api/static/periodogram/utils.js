export function linear_to_log(
  value,
  base_min = 0,
  base_max = 100,
  target_min = 0.05,
  target_max = 500,
) {
  const lin_min = Math.log(target_min);
  const lin_max = Math.log(target_max);

  value = (value - base_min) / (base_max - base_min);

  value = value * (lin_max - lin_min) + lin_min;

  return Math.exp(value);
}

export function log_to_linear(
  value,
  base_min = 0.05,
  base_max = 500,
  target_min = 0,
  target_max = 100,
) {
  const lin_min = Math.log(base_min);
  const lin_max = Math.log(base_max);

  value = Math.log(value);
  value = (value - lin_min) / (lin_max - lin_min);
  value = value * (target_max - target_min) + target_min;

  return value;
}
