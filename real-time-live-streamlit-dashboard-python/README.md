# Real Time Live Streamlit Dashboard

For this project, I implemented a small real-time live Streamlit dashboard to display some information about the glucose readings. It is a very small component that I wanted to include to make the project more complete. As the glucose readings we are simulating are being sent to the **raw_glucose_readings** event hub, they are also being consumed by the Streamlit Application. The Streamlit application is then processing the data and displaying it in a user-friendly manner. The dashboard is updated in real-time as new glucose readings are sent to the event hub.

Diagram of the Real Time Live Streamlit Dashboard Architecture:

![image](/images/Real-Time-Dashboard-Diagram.png)


Below is an example of what can be seen when running the Streamlit Dashboard:

![image](/images/Dashboard_3.png)

As you can see in this one, the geographical map is showing the locations of the users as the event data contains the latitude and longitude of the users. This image is consitent with location that I have set in the simulation. As said in the [Scenario section](../README.md#scenario) **the hospital and the patients are located Within Spain, so the map is showing the patients in Spain**. The simulation ensures that this aspect is consistent.


More examples of the dashboard can be seen below:
![image](/images/Dashboard_1.png) ![image](/images/Dashboard_2.png) ![image](/images/Dashboard_4.png) 
