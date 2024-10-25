// eslint-disable-next-line no-undef
db.createUser({
  user: "mongo",
  pwd: "mongo",
  roles: [
    {
      role: "dbOwner",
      db: "database",
    },
  ],
});
