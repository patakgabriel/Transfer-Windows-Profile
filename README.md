# Scenario

I worked in a project to upgrade/replace computers with Windows 7 to Windows 10. 
I noticed that our current process involved manually copying and pasting the user profile ("C:\Users\PROFILE") from the old computer to the new one.
This was a very slow and innefficient process because it took time to find these folders, figure out what profiles needed to be copy, and connecting to the new computer to drop the files.

I know there are many tools in the current market and even Windows includes a tool to restore profiles. Some programs took too long backed up more things that we wanted to and other programs required enterprise licenses like Liquidware. However, there was no solution in the horizon so I decided to build my own.

# Solution

I created a script that could automate transferring profiles with a GUI. It would ask for admin credentials, the old computer name, the new computer name, and what profiles you wanted to copy.
The script also used multiprocessing to run parallel transfers to allow the technician to transfer profiles from as many computers as needed.
The tool was a huge success within our department allowing us to complete the project faster and efficiently.
