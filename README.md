# Memento

## Inspiration
With this hackathon, we knew that to make an impact, we would need to create something that gave back to our community, was scalable, and made an impact in the medical field. In 2023, Grant's grandfather Jere was diagnosed with Alzheimer’s disease. His grandmother has since become an advocate in the city of Cincinnati OH, participating annually in the Alzheimer’s Association Walk to End Alzheimer’s, even appearing on the televised news to spread awareness of the disease. 

After having a conversation with Grandmother about the effects Alzheimer’s has had on his grandfather Jere in the past year, we came to realize that there were many persistent and pervasive unmet needs related to making those with the disease more independent, assisting in caregiving roles, and allowing clinical teams to access qualitative data.

With this issue in mind, we asked ourselves:   How might we develop an app-based integration that serves to aid caregivers and those with the disease, while also contributing to Alzheimer’s clinical research?
## What it does
Introducing Memento, a digital journal for those with degenerative cognitive diseases. Memento aims to act like a long-term memory, retaining knowledge of the information provided in the user’s journal entries. Memento can be fed images, audio recordings, and locations to form a coherent summary of your life, and can be easily accessed by asking Memento a question in the “chat” section of the app. 
This supplies patients and their caretakers with a daily view on the home page (most recent on the top), and a weekly/monthly/yearly view in the library page. This would assist someone who may be confused to simply pull up the previous day’s activities, serving as an archive of their day-to-day routines and events that are special to them, and ultimately providing them with independence and more structure. 
Finally, the qualitative and quantitative data (i.e frequency of repeatedly asked questions in the chat feature) can be relayed to the patient’s healthcare provider to track worsening symptoms & progression of illness.
## How we built it
We built this through a combination of React.js, Python, Flask in Python, and Postgres supported by Tembo. Our AI assistant built off of KeyBERT and GPT3.5-turbo-0125 allows us to generate personalized and human answers from the journal entries stored in Tembo. We also used Figma to prototype and design all the UX/UI elements.
## Challenges we ran into
This project is very complicated by nature because not only are we trying to make the user experience intuitive, but we are also trying to use the journal data stored efficiently and effectively. Initially, our plan was to use ReactNative through Expo (cloud-based platform for mobile app development) but we encountered multiple issues regarding styling and IOS optimization in general. We then pivoted to XCode for a short period of time but because of our lack of experience in SwiftUI, we found that we could not support our core functionalities. We eventually came to React.js to build a web app that is scaled for mobile with all the aforementioned functionalities. To compensate for the lack of a native mobile app, we replicated our vision as closely as possible in the time frame we had via Figma to show the UX/UI elements.

One other issue we ran into while trying to host our text processor on the cloud was that the Google Cloud Run kept running out of system memory (we were limited to 8GB of system memory) and we had to then switch to a proxy server. In theory, the code should plug and play into Google Cloud Run, BUT we weren't able to do that due to memory limitations.

## Accomplishments that we're proud of
Successfully setting up all the core functionalities we were aiming to tackle, including being able to provide non-robotic, emotion-based responses to very distraught patients.
We were able to seed a dataset of 7 days to show off the capabilities of both the journaling, picture storage, and the assistant querying to effectively help the user recall and connect memories.
One major win was the successful setup of Tembo and learning how to vectorize a table by creating a job that would return us entries related to keywords.
## What we learned
We are horrible when it comes to implementing it natively in a web app. Jokes aside, we learned a lot about how Swift works through Xcode and also how Expo works through React Native. None of us have ever tackled the front end from a "make it look pretty/usable" perspective, so this was a huge learning journey, both through market research on how UI is designed for certain age groups and also about implementing it in a reusable manner.

From the Design side of things, this was the first time trying to make a very polished demo of an app as opposed to just a rough concept sketch. Even though our team comp was not suited for XCode/ReactNative development, we are very proud that we tried to. The workshop hosted by NIS (Next Innovation Scholars) allowed us to create different solutions by imagining different futures where the well-being of Alzheimer's patients had improved. 


## What's next for Momento
Using the Figma mockup we have, we would like to create an IOS version of what we have so far as well as create more views for both the caretaker and flashbacks. Within our doctor view, we would explore ways to correlate vitals to certain aspects of cognitive research. We would also like to host our AI code online instead of locally. This would allow us to handle multiple clients at a time as well as make future updates easier. One of the things we were inspired by was Apple's IOS 17 journal app which allows for journal entries with location tags and pictures. This would make journal entries much easier for the elderly and help provide us with more data for MomentoAI.

Another aspect we would like to add to the app is support for other types of data. This is because there is a [https://news.harvard.edu/gazette/story/2020/02/how-scent-emotion-and-memory-are-intertwined-and-exploited/](https://news.harvard.edu) Harvard study showing that our senses are connected to our emotions and certain memories. Our app would be able to record all instances where the user had a sudden burst of memories linked to certain environmental stimuli and act as a portal to enable them to visit similar memories by replication of similar stimuli.

Lastly, using the journal entries/ location data/ contact proximity/ doctor notes integration, we could help the user form a healthier routine and be notified of medicine timings.
