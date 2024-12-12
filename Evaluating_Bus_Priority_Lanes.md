### Evaluating Bus Priority Lanes in 2 Intersections in Cambridge, Watertown and Sommerville, MA

#### Background
Belmont and Mt. Auburn Streets in Cambridge and Watertown, served by MBTA Routes 71 and 73, faced frequent delays due to traffic congestion. In late October 2018, bus/bike queue-jump lanes and transit-signal priority were introduced at three intersections, reducing travel times significantly. Similarly, on Broadway in Somerville's Winter Hill neighborhood, MBTA  bus-only lanes and signal priority were implemented between August and October 2019, on corridors served by Routes 89 and 101.
These efforts were supported by the cities' mayors, despite some local opposition.

#### Objective
To determine the general impact on level of service and on riders experience of these infrastructure changes on bus service on MBTA bus routes 71, 73, 89 and 101. Time of day and seaonal variability should be addressed. The analysis should be presented in a way that is interpretable by a public policy advocacy group interested in public transit reliability and quality issues.

#### Datasources
AVL data from the MBTA for stops immediately around the affected intersections has provided from 2015-2019.  

#### Data Processing 
Several data processing steps are needed to generate meaningful analysis from this data. Several of these are metrics that are calculated in order to draw meaningful conclusions about the impact on bus service.

1. The evaluation period that must be assigned to each record is different depending on the intersection, since the infrastucture was implemented at different times
2. Headway is calculated as the difference in seconds between observations at the same stop for sequential trips on the same 3. day.
3. Coefficient of Variation (CV) of headway, a common metric for quantifying headway reliability for a given route, direction and time period is calculated according to the following formula:

**Coefficient of Variation (CV):**

CV = sigma/mu

Where:
- sigma is the standard deviation of headways.
- mu is the mean of headways.


4. An additional corridor-level dataset was created from the stop-level dataset that computes running times in each direction over the entire route corridor affected by the TSP infrastructure. If the first and last stop of the corridor is not observed in the avl for that trip, the trip is eliminated from the data.


#### Findings

The application at https://mbta-bus-priority-eval.streamlit.app/ can be used to evaluate the infrastucture changes to stop and corridor level running times, as well as stop level coefficient of variation of headway. The filters on the left hand panel can be used to see the data at different time periods.

Median Running Times (in seconds) By Corridor, AM Peak
| Route, Direction | Median Runtime (Before) | Median Runtime (After) |
|-------------------|--------------------------|-------------------------|
| 89, inbound      | 402                      | 339                     |
| 89, outbound     | 297                      | 240                     |
| 101, inbound     | 416                      | 342                     |
| 101, outbound    | 267                      | 221                     |
| 71, inbound      | 904                      | 629                     |
| 71, outbound     | 615                      | 589                     |
| 73, inbound      | 925                      | 635                     |
| 73, outbound     | 574                      | 563                     |



##### Implications of Peak Travel Time Savings on the Mt. Auburn St. Corridor

The full cycle time C is calculated as: C = t_1 + r_1 + t_2 + r_2. Travel time savings reduce t_1 and t_2, leading to a shorter cycle time (C). Shorter cycle time means that the number of busses required during peak period is diminished, since:

peak busses = C/headway

If headway remains constant and C is reduced, the number of peak busses is reduced. Alternatively, if the number of peak busses is held constant, headways can be reduced. Reducing the number of peak busses can free up capital and labor hours for use elsewhere i te system, perhaps reducing the headways on another route. Reducing the scheduled headway generally provides a better level of service for the rider, and increases reliability. 

Travel time savings in the Mt. Auburn St. corridor present an opportunity for the MBTA to revise Routes 71 and 73 schedules. Shortened cycle times can reduce peak bus requirements, optimize recovery times, and allow for increased service frequency or cost savings. However, more significant analysis should be done using data from the entire system to substantially investigate these tradeoffs.

#### Future Work
This project was time constrained, but with additional resources I would have added the following:
1. a user interface for comparing explicitly certain time periods (ie: the differences in distribution of CV of headway between AM and PM peak for route 89)
2. Integrate AVL data for more of the system so that we can more rigorously analyze the impacts of travel time savings over the course of the network, and analyze downstream effects.
3. Coefficient of variation of headway can be integrated with other data to develop a notion of decreased wait time, which is a valuable interpretable statistic when thinking about the impact of infrastructure changes on riders.