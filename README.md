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

### Labelling

The labelling button will direct you to the labelling app, an open-source project known as VGG Image Annotator (VIA). The documentation for VIA can be found in the 'Help' tab under 'Getting Started' and on the official VIA website. To save an image with its annotation(s), click the “save project” button (middle of the sidebar).

### Overview

Allow users to view annotation logs: If a user saves a new annotation, it will be recorded here, along with the image name and a boolean indicating whether the image has annotations or not. Clicking on the image will redirect the user to VIA, where they can annotate the image.

### Help

Redirect users to a form to write their issue(s).

### Settings

Allow users to change some settings on the app.

### Administrator Privileges

Administrators can access: {URL}/admin/user_management. Here, they will find a list of all users and have the ability to change a user's role to admin, and an admin's role to user. They can also delete any user.

**Note:** ADMIN SHOULD NOT BE REMOVED AS ONLY THEM CAN CREATE A USER (Or if the database is empty,
