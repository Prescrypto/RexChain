# Introduction

### How to contribute to Rexchain

First off, thank you for considering contributing to Rexchain.  
Feel welcome and read the following sections in order to know how to ask questions and how to work on something.   
Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

As for everything else in the project, the contributions to Rexchain are governed by our [Code of Conduct](https://github.com/Prescrypto/prescrypto_foss_code_of_conduct/blob/master/CODE_OF_CONDUCT.md).

### Support questions
Please, don't use the issue tracker for this. You can contact us at info@prescrypto.com we will anwser back as soon as we can.

### Reporting issues
Report bugs at https://github.com/Prescrypto/RexChain/issues.  

If you are reporting a bug, please include:
* Your operating system name and version.  
* Any details about your local setup that might be helpful in troubleshooting.  
* If you can, provide detailed steps to reproduce the bug.  
* If you don't have steps to reproduce the bug, just note your observations in as much detail as you can. Questions to start a discussion about the issue are welcome.  

### Submitting patches
Please use Flake8 to check your code style. You may also wish to use Black's Editor integration.
Include tests if your patch is supposed to solve a bug, and explain clearly under which circumstances the bug happens. Make sure the test fails without your patch.
Include a string like "Fixes #543" in your commit message (where 543 is the issue you fixed). See Closing issues using keywords.

### First time setup
__Download and install the latest version of git.__

__Configure git with your username and email:__

git config --global user.name 'your name'  
git config --global user.email 'your email'  

__Make sure you have a GitHub account.__  

__Fork Rexchain to your GitHub account by clicking the Fork button.__  

__Clone your GitHub fork locally:__    
git clone https://github.com/{username}/Rexchain  
cd rexchain  

__Add the main repository as a remote to update later:__  
git remote add Prescrypto https://github.com/Prescrypto/RexChain
git fetch prescrypto

__Create a virtualenv:__  
python3 -m venv env  
. env/bin/activate  
 or "env\Scripts\activate" on Windows  

### ...The complete guidelines would be able soon :) 
