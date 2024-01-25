# f23_team_20

## Personal Organizer and Management Website - LifeSync

### Overview 
LifeSync will be a website that is designed to help individuals efficiently manage their tasks, appointments, and responsibilities. It serves as a centralized system for planning, tracking, and organizing various aspects of one's life. 

### Team Members
* Mahima Borah (mahimab)
* Sambhav Jain (sambhavj)
* Zhichen Li (zl3)

### Requirements

* Django
* Django-allauth
* Markdown
* Cryptography

### Django admin setup

Recommended (Python _**selenium**_ required):

| OS            | Script   | Requirement                                        |
|---------------|----------|----------------------------------------------------|
| Windows       | init.cmd | 7 w/ Powershell, 8.1+, Windows Server 2008 R2 SP1+ |
| Linux (MacOS) | init.sh  | -                                                  |

Manually:

1. Go to http://127.0.0.1:8000/admin/ and login with credentials
2. Under social accounts, add a new social account 
3. Details
* Provider: Google
* ProviderID: 1
* Name: lifesync-app
* ClientID and Secret key: From https://console.cloud.google.com/apis > Project lifesync > Credentials
