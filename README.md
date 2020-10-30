# TTRobot

# Setup
# World File
The world file ( tt_robot/worlds/Table_Tennis.world ) was created using an empty world with two models. The table is a modification of 
the table model in the the standard gazebo models file. The table tennis ball was created to be the size of a standard table tennis ball 
with friction coeeficient(0.3) and coefficient of restitution(0.6) to mimic a real table tennis ball. The ball model has a plugin 
( gazebo_plugin_tutorial/model_push.cc )  that resets it pose and velocity after a certain time interval ( 2 seconds ). It is currently set to 
a single pose and trajectory which shall be extended to a random selection from a predefined sample set.
