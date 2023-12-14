# Intradys

## Introduction

Intradys is a web application designed for manual image annotation, as well as automatic image annotation through AI. It enables users to verify and modify the annotations predicted by the AI as needed. You will need to be logged in to be able to use the Intradys app.

## Usage

### First User

The first user will be created whenever someone reaches the logging page. It will create the admin account with the following credentials:
- Username: admin
- Password: admin

This account can then create another admin with a different username and password and then safely delete the first admin account.

When successfully logging in, the users will be directed to the home page.
![Neuravisionix Homepage](https://github.com/Artemis-IA/Neuravisionix-Pioneers/blob/fred/docs/homepage.png)


### Overview

Allow users to view annotation logs and allows users to annotate an image : If a user saves a new annotation, it will be recorded here, along with the image name and a boolean indicating whether the image has annotations or not. Clicking on the image will redirect the user to the the annotation app, an open-source project known as VGG Image Annotator (VIA), where they can annotate the image.

The documentation for VIA can be found in the 'Help' tab under 'Getting Started' and on the official VIA website. To save an image with its annotation(s), click the “save project” button (middle of the sidebar).
![Neuravisionix VIA](https://github.com/Artemis-IA/Neuravisionix-Pioneers/blob/fred/docs/via.jpg)
### Help

Redirect users to a form to write their issue(s).

### Settings

Allow users to change some settings on the app.

### Administrator Privileges

Administrators can access: {URL}/admin/user_management. Here, they will find a list of all users and have the ability to change a user's role to admin, and an admin's role to user. They can also delete any user.

**Note:** <span style="color:red">ADMIN SHOULD NOT BE REMOVED AS ONLY THEM CAN CREATE A USER (Or if the database is empty, the admin account admin/admin will be created).</span>

### Databases

The images and the annotations are stored in a MongoDB database, and user’s credentials are stored in a MariaDB database. MariaDB is a basic choice for users. We use MongoDB since we have a JSON with the annotations, and MongoDB can easily be given a JSON.

## License

### VIA License

[BSD 2-Clause License](https://en.wikipedia.org/wiki/BSD_licenses#2clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29)

Copyright (c) 2016-2017, Abhishek Dutta. All rights reserved. Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
- Redistributions of source code must retain the above copyright notice, this list of conditions, and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions, and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
