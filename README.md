# Distributed_System_L1_Python
Building Distributed Servers (Distributed Blackboard)


## Distributed Blackboard
- A web application running on multiple
(distributed) servers.
- Clients can connect to any server and
post information via a web browser.
- Server should store all data received,
and display it.
- A web application running on multiple
(distributed) servers.
- Clients can connect to any server and
post information via a web browser.
- Server should store all data received,
and display it.
- Client data must be seen from any
server
  - Propagate information to all boards.
  - In a peer-to-peer-manner
  
### `How it looks!`
![screenshots1](/img/ds1.png?raw=true "screenshots1")

#### Task one is to make it work:

- Implement Add in the distributed blackboard by creating POST API
- Create script for client can post 5 messages at the same time from any server.
![screenshots2](/img/postentry.jpg?raw=true "screenshots2")

#### Task two modify/delete:

- Implement modify/delete in the distributed blackboard by creating modify/delete APIs.
- Scenario:
	- Client connects to server 1, and posts 5 messages.
	- Client connects to server 2 and modifies 1 message.
	- Client connects to server 3 and deletes 1 message.
	- Client connects to server 4 and should see 4 messages, with one modified.
![screenshots3](/img/propgatepost.jpg?raw=true "screenshots3")

#### Task Three is to ensure Consistency:

We need to make sure that any post request from any server has to be delivered to all server with the same order.
For example if client 1 connects to all servers and posts 5 messages to each, concurrently, then 5 messages should be deliverd to all servers and shows the same order. 

![screenshots4](/img/concurrentsend.jpg?raw=true "screenshots4")

