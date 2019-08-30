# Installation

## Prerequisites
- you will need a copy of your database.sqlite file in the folder with the code
  - I hard link to a copy in my nextcloud repo, however then I need to run this with sudo
- There are some custom views that need to be added to the database to make this work, they are in the sql folder
  - If you use the sample database these views are already created and this step is not necessary.
  - this command will run them for you: 
      `$ sqlite3 database.sqlite -init init_views`
  - You can delete the SQL folder and the init_views file once this is done
- Optionally you will want the resources directory copied there too
  - I soft link to the resources directory in my nextcloud repo

## Execution
- the start script shows how to run it - I need to sudo as my database.sqlite is a soft link to a copy of my db in my nexcloud server. It can run without sudo if this is not the case for you
- the initial username/passwd is admin/admin. ** Security is a WIP and at rpesent the only way to update users is directly in sqlite3**
If you find yourself here and have any interest in this then get in touch and I'll work with you to get it going.
