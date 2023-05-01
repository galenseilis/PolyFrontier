# PolyFrontier
PolyFrontier is an engineering school project that simulates two major features of [The Smart Border](https://www.douane.gouv.fr/fiche/brexit-smart-border) project.

# Contributors : 
[Loic Madern](https://github.com/LoicMadern)  
[Nabil Abbar](https://github.com/ABBARNABIL)  
[Nicolas Lacroix](https://github.com/NicolasLacroix)
[Stanley DINNE](https://github.com/StanleyDINNE)  
[Yassine Boukhiri](https://github.com/yboukhiri)
  
## Extensibility & Interoperability
PolyFrontier offers an API that communicates with external systems. It gives information and predictions of the traffic at the border to transport companies and other developers. It is also able to connect to APIs and various data ressources in order to get the data.

## Traffic forecast
Also, PolyFrontier can predict the flow of the incoming and outgoing traffic in order to anticipate peak periods as precisely as possible. The system takes into consideration many factors to come up with the best predictions: date, weather, cultural or sporting events, the evolution of the health crisis, political announcements, strike or blockage of roads or ports, etc.


## User stories
User stories are mostly features that bring value to different personas. A user story must follow INVEST principle and be vertical. In our project, user stories are presented as issues. Some user stories are technical, which mean they only improve the nonfunctional aspect of the system. 

### Definition of ready
A user story is ready to be implemented if : 
- It has a description
- It has an acceptance criteria
- It has at least one acceptance test 
- It has an estimate in points 
- It has a Moscow category

### Definition of done
A user story is done when : 
- all acceptance tests pass
- The user story is integrated on **dev** branch
- New and old unit tests pass 
- The full build passes

## Contributing 
The branching structure of the project is as follows : 
#### main
This branch has an infinite lifetime. It is very stable and production ready.
#### dev
This branch has an infinite lifetime and it is stable too. Periodically, this branch is merged into **main** and tagged with a label that shows the release version.
#### <featurename>
Feature branches are created to implement new features. Those branches are very unstable. They are merged into **dev** when the developer finishes implementing the corresponding feature and makes sure all acceptance tests pass, the old tests still pass and the full build passes. 
### To contribute :
Contributors must first choose a user story from the issues to implement. Then they should create a branch with the following **naming convention** : 
Let's say github generated **#33** for the issue **"Adding traffic prediction system"**. The name given to the issue to be created is : **33-adding-traffic-prediction**. But in case, the branch is already created, they should contact the person that created it so they could collaborate. After coding the feature, the developer must integrate his work by merging his branch into **dev**. Then they can delete their branch. 
