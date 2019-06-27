# Documentation ARM Data Science Project
## First Meeting and Launch of the Project
### Meeting Tao Dou, our contact from ARM's Cambridge office on the 2nd of May.

We were given a presentation of the project including the data we would be given, ARM's workflow regarding the treatment of the data, and what was expected from us. We got to ask questions to clear up some unclear points and signed an NDA without which we could not get hold of the data. This was also the first meeting for the team, which gave us the opportunity to learn about the different skillsets present within the team. This gave us a rough idea of who would be working on which aspects opf the project. Indeed, it seemed like the most efficient solution to split the workload since the work could be separated in independent tasks. Thus, it was decided that one group would focus on the preprocessing, whilst the other would begin exploring the different available options for the GUI.
At first, not much time was spent on understanding the data visualization and data science parts. Regarding visualization, the plots that ARM expected from the dashboard were given to us by ARM in their sample report, and the implementation of these graphs required having the data in a table, hence having finished the preprocessing part of the project. For the data science part, preparatory work and research were carried out but once again, the implementation of the algorithms could not be done until preprocessing was at least partly done.
Moreover, given how complex the testing processes are, a large portion of the work involved analysing the data logs to understand the meaning of the various test names. We exchanged emails with Tao and Chris and set up a meeting to discuss progress and obtain more information about the data.


## Second Meeting and Follow up questions
### Skype with Chris Hawkins, ARM's engineer on the 16th of May.

We were given the chance to ask Chris about the following questions relating to our project:
1. Missing Perl Scripts needed for Yield/Vddmin data, and additional information about their behaviour.
2. ARM's preferences regarding the dashboard (Website, Application, etc..).
3. Further data logs needed in order to generate Back Annotated data (not available in the end).
4. Expectation of the scope of the project (data set, sections, etc..).

## Third Meeting and more questions
### Skype with Chris Hawkins and Tao Dou on the 24th of May.

More questions in depth were asked about the pre-processing and data science part of the project. This meeting was centered more around the technical expectations of the data science part, the expected outputs of the Machine Learning models and some advice on model families to explore. This session also focused more on the Memory Cells, which had been less thoroughly analysed than the Standard Cells since their architectures and parameters were highly complex to understand. Since the processes applied were very similar, it seemed like a promising strategy to get the SC models working and then transpose them to the Memory Cells.


## Project update on the 28th of May.
The dashboard building started, using PyQT5 and Qt Designer. Since ARM did not request a website, an application was built, which made the process of linking python code with the GUI much more intuitive than with a website. This approach made it simpler to reuse the application on a new dataset, and from any device, since it did not require the data to be uploaded to a server. Furthermore, using an executable app made maintenance much simpler than if a website was used. Finally, using an application meant there was no need to get third parties involved (to host servers for example) and helped keep the whole project open-source and very approachable. Of course, ARM could easily convert the dashboard to a website if they were to incorporate it to their current process.
We also designed a much more efficient pre-processing method which siginificantly shortened the time preprocessing the data took, see poster above for more information. 


## Fourth Meeting 
### Received feedback from Dr. Cilbert + Skype with Chris Hawkins and Tao Dou on the 6th of June.


#### ARM Data Science and Visualization Leaflet Front View
![Image Text](https://github.com/tanyuzhuo/arm/blob/master/Images/ARM%20leaflet%201.PNG)

#### ARM Data Science and Visualization Leaflet Back View
![Image Text](https://github.com/tanyuzhuo/arm/blob/master/Images/ARM%20leaflet%202.PNG)

We recevied very positive feedback about the leaflet and poster both from our client ARM and our supervisor Dr. Cilberto. Few changes were made about the design including size of fonts and graphs. Questions about data visualization were answered during the skype call. Last changes were brought to the Machine Learning models and graphs were polished.


## Project update on the 7th of June.

The group has started to work on merging each parts of the project together. Progress was updated daily between group members and support was received actively. The main focus of those last few days was merging the codes used in the Data Science  and GUI Design parts, since different nomenclature was used by the two groups. Moreover, some graphs were difficult to include in the dashboard, and required some effort to be incorporated. Finally, efforts were made to make the code as adaptible as possible to new data, although with some supervision. In addition to this, the final version of leaflet was designed and printed out in hard copies for the hackbooth presentation.

## Project update on the 12th of June.
### Last day before Hackbooth.

#### ARM Data Science and Visualization Poster
![Image Text](https://github.com/tanyuzhuo/arm/blob/master/Images/ARM%20poster.PNG)

The dashboard prototype has been finalised and is ready to be presented at the Hackbooth event. We have practiced and prepared a short presentation briefing on our project including an introduction and three main elements of the project. Poster and monitor has been requested and set up.

## Material Used, Sustainability Report, and Ethical Consequences
The project only involved software, thus the only material used were our personal laptops and the prining services offered by the department for the leaflet and hackbooth. From a sustainability point of view, there is not much to say given that the project was fully software based. Perhaps having opted to build an application rather than a website reduced emissions linked to storing the website and data on a server, but that sounds very unlikely. Were the application to be used by ARM in its chip design process, and the number of chips designed and tested by ARM reduced, the product could have a legitimate inpact on ARM's environmental impact. There are no ethical consequences linked to this project. It's impact is narrow, limited to a specific group of ARM employees, and has no other economic or social impact.
