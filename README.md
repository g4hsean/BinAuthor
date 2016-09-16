# BinAuthor

BinAuthor is an IDA pro plugin developped through research at concordia in the area of binary authorship identification. The main purpose of this tool is to apply cutting edge research 
in order to solve the difficult task of matching an author to a provided unknown binary. Our tool achieves this by applying novel techniques such as statistical analysis and clustering algorithms
in conjunction with constructed features to match an author to an unknown binary.

# Installation

###Requirements:

**OS:** windows (any version supported by IDA Pro 6.8 or higher) other operating systems coming soon
**Python:** 2.7 64 bit version
**MongoDB:** Any version with WiredTiger

To install the BinAuthor IDA Pro plugin you should follow the steps below:

**Step 1:** Clone the BinAuthor repository to a location of your choosing

**Step 2:** Enter the BinAuthor->Installer->Dependencies directory and install git and VCForPython27

**Step 3:** Download from the internet MongoDB for x64 systems

**Step 4:** navigate to BinAuthor->Installer directory and run BinAuthor-Installer.py as Administrator <- ****IMPORTANT****
        and follow the installation instructions. (note folder dialogs need only the root folder of both idapro and mongodb ie. IDA Pro 6.8 and MongoDB folders)
        Note: If no errors are encountered during the install process then proceed to step 5 otherwise contact the Binauthor
              Developer team.
**Step 5:** Navigate to the Desktop and click on the BinAuthor_MongoDB_Start.bat file to start mongoDB

**Step 6:** Load IDA Pro if there are no error dialogs about the plugin then everything is set up.

**Step 7:** Follow the below instructions for plugin usage.

# Basic Usage

###Creation of Initial Author Database:

In order to obtain a list of potential authors of an unknow binary you must start with a training set. What this means is you must have a database filled with signatures of code created by known specific
authors. To do this you open up IDA Pro and then click BinAuthor->Author Indexing and a new window opens. This new window allows you to choose to either index a single author or multiple authors. Since 
this is the first time the tool is run, we would like to create our dataset to which we will use for identifying the authors of unknow binaries. To index more than one author you must create a parent 
folder (AuthorsDirectory) with a subfolder structure like the one below:

![alt tag](https://github.com/g4hsean/BinAuthor/blob/master/FolderStructure.JPG)

Once you have created the folder structure and added all of the authors and their coresponding binaries the next step is to index them. With the new Author indexing window still open click on the 
select folder button and select the parent directory (in this case AuthorsDirectory) where the author subdirectories are located. Next since we are indexing more than one author we must select the
"Label Using Multiple Authors" radio button to use the folder names as author names. Finally click the index authors button at the bottom. What you will see are some terminal windows open up and the 
indexing will commence. Once the indexing has finished the terminal windows should close and you are back to the author indexing window of BinAuthor. Thats all there is to author indexing.

###Capturing of Author Features From Binary:

To capture some or all of the features without using the author indexing portion of the plugin you can just choose to run any of the following menu items: Quality Features, Code Organization Features,
Generalization Features or Variable Utilization Features. These menu items when combined are what the author indexing part of the plugin uses to store author features to database. The ability to select
only certain features to index gives the analyst a high degree of control over what features they may find useful for their needs. Some analysts may find that using all features produces the best results
whereas others may find it necessary to use only certain features to obtain excellent results.

###Identifying The Author of An Unknown Binary:

Now comes the part everyone has been waiting for, identifying the author of a binary we suspect to have a fingerprint for in our database. The prerequisties for this stage are that you have followed the
"Creation of Initial Author Database" section of this manual and have an author fingerprint dataset to compare your unknown binary to. To identify the author of a binary open in IDA pro simply click on
the BinAuthor IDA Pro menu and select Author Identification. Wait some time for the plugin to create the features and compare them to the authors stored in the database. If everything goes well you now
have a new window which shows you which authors are most likely to be the author of the binary open in IDA Pro (The table at the top labeled "Author Identification") as well as some information about
the feature metric scores obtained (The table at the bottom labeled "Author Identification Metrics"). The Author Identification table shows you the top candidates BinAuthor believes are the author of the
given binary. The percentage values to the right of the author name gives you the confidence that BinAuthor has at matching the given binary to the specific author. Obviously the more binaries you have
for each author the higher the confidence scores will be. Generally the top 3 candidates will contain the author of the unknown binary for small author datasets stored in your database. Finally the Author
Identification Metrics table will show you which of the features are providing the best results for matching in the event you want to fine tune the plugin to focus more on one feature over another. It will
also help an analyst see why the Authors in the Author Identification table were given such scores.

###Function Labeling:

In order to ensure that BinAuthor extracts,stores and computes features only belonging to an author our tool must identify only functions that were written by the author. Filtering functions based on if
an author wrote them or not has a benefit of reducing false positives when storing and comparing author signatures. The side effects of the research to identify only functions written by an author are
that we have also found ways to identify compiler functions and other functions that we deem as compiler helper functions since they are very short snipits of code (usually even a function with one
line of code has a large code size at the assembly level). This means that when navigating the BinAuthor menu and selecting "Function Classification" we get to see a graph with the distrobution of User,Compiler
and other functions. The function classification algorithm also colors the functions found under the function list in IDA Pro which allows a reverse engineer to only focus on user code and not compiler code. The color
scheme is as follows: Green = User Functions, Dark Blue = Compiler Functions, Burgandy/Brown = Other functions (compiler helper functions). Finally on the left hand side of the function classification
pie chart graph we see a list of function classes. Clicking on any of these classes will show the functions that were identified to belong to the selected class. Double clicking on a function will bring you
to a new window which shows the statistical features which are used to identify the class the currently selected function belongs to. The final graph labeled the "Function Correlation" graph is very useful
in the event you believe a function has been missclassified. The function correlation will show you using statistical correlation which functions closely resemble the current function selected. The functions
with strong correlation to the selected one will be shown and if those functions belong to a different function class then it is likely the selected function was improperly classified. This statistcal overview
provides to an analyst fine grained information about how a given function is classified and can be used in the even that the analyst would like to fine tune the function classification algorithm.

