# CatGenie A.I. By Petnovations
Home Assistant Integration for Petnovations CatGenie A.I. using their Public API.

Due to limitations yet with authenticating with your account phone number, you'll first need to installing a tracer tool to get your refreshToken by sniffing the traffic of the CatGenie A.I. mobile app. I was able to get the refreshToken myself using my MacBook M1 by first installing 'Requestly' (similar to wireshark). From there, I installed the CatGenie A.I. app to my MacBook, and was able to trace the traffic to obtain my refreshToken. 

Obtaining your refreshToken is important as this will be used every 15 minutes to refresh your access token that will be used to access the Petnovation API endpoint. You'll need this in order to configure your integration.

I hope to improve the integration in the future to allow for direct authentication with an account 'phone number' and having it authenticate with MFA (text message) as it does currently with the mobile application.

Version v1 of this mobile application will be focused primarily on building proper sensors, and working further on integration setup. I plan to work on switches and being able to control the CatGenie A.I. configurations (running manual cycles, adjusting settings, etc) once most of Version 1 is fleshed out.

Thanks Again

@bensoae87 at PrimeAutomation 

![](https://github.com/PrimeAutomation/petnovations/blob/main/example.png)

