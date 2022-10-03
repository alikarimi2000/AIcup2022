all:
	#Options:
	#	DEBUG_NO_BRAINER


DEBUG_0:
	python3 $(ANALYZOR) $(SERVER) 10 $(CLIENT_DEBUG) $(CLIENT_0)

DEBUG_1:
	python3 $(ANALYZOR) $(SERVER) 10 $(CLIENT_DEBUG) $(CLIENT_1)

DEBUG_2:
	python3 $(ANALYZOR) $(SERVER) 10 $(CLIENT_DEBUG) $(CLIENT_2)

DEBUG_3:
	python3 $(ANALYZOR) $(SERVER) 10 $(CLIENT_DEBUG) $(CLIENT_3)

DEBUG_4:
	python3 $(ANALYZOR) $(SERVER) 10 $(CLIENT_DEBUG) $(CLIENT_4)

DEBUG_5:
	python3 $(ANALYZOR) $(SERVER) 100 $(CLIENT_DEBUG) $(CLIENT_5)

DEBUG_6:
	python3 $(ANALYZOR) $(SERVER) 10 $(CLIENT_DEBUG) $(CLIENT_6)

DEBUG_7:
	python3 $(ANALYZOR) $(SERVER) 100 $(CLIENT_DEBUG) $(CLIENT_7)

DEBUG_8:
	python3 $(ANALYZOR) $(SERVER) 100 $(CLIENT_DEBUG) $(CLIENT_8)

DEBUG_9:
	python3 $(ANALYZOR) $(SERVER) 100 $(CLIENT_DEBUG) $(CLIENT_9)

DEBUG_10:
	python3 $(ANALYZOR) $(SERVER) 1000 $(CLIENT_DEBUG) $(CLIENT_10)

DEBUG_11:
	python3 $(ANALYZOR) $(SERVER) 100 $(CLIENT_DEBUG) $(CLIENT_11)

DEBUG_12:
	python3 $(ANALYZOR) $(SERVER) 100 $(CLIENT_DEBUG) $(CLIENT_12)



ANALYZOR=./analyzer.py
SERVER=./src/server.py

CLIENT_DEBUG=./Clients/Python/main.py

CLIENT_0=./AIBank/0_no_brainer/main.py
CLIENT_1=./AIBank/1_random_navigation/main.py
CLIENT_2=./AIBank/2_patrol_plus_approach/main.py
CLIENT_3=./AIBank/3_better_ppa/main.py
CLIENT_4=./AIBank/4_retriever_1/main.py
CLIENT_5=./AIBank/5_badass_brawler/main.py
CLIENT_6=./AIBank/6_better_badass/main.py
CLIENT_7=./AIBank/7_gallent_knight/main.py
CLIENT_8=./AIBank/8_gladiator/main.py
CLIENT_9=./AIBank/9_veteran/main.py
CLIENT_10=./AIBank/10_hero/main.py
CLIENT_11=./AIBank/11_lord/main.py
CLIENT_12=./AIBank/12_LEGEND/main.py


