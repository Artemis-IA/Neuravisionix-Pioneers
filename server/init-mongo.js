  db = db.getSiblingDB('bdd_label');
  db.createUser(
      {
          user: "user",
          pwd: "password",
          roles: [
              {
                 role: "readWrite",
                 db: "bdd_label"
              }
          ]
      }
  );
