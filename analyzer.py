import json
import os
import os.path
import subprocess
import shutil
import pathlib
import sys
import time

SERVER_PATH:str = "./src/server.py"
CLIENT_1_PATH:str = "./Clients/main.py"
CLIENT_2_PATH:str = "./Clients/main.py"
CLIENT_LOG_PATH:str = "./Clients/Python/Clients/logs"
SERVER_MAX_RUN_COUNT:int = 100

def panic(error_message:str) -> None: # same as throw
    print("Panic!: ",error_message)
    sys.exit(1)


if len(sys.argv)<=2:
    panic("Invalid number of arguments \n"+(
        "arg 1 : server path\narg 2 : server iteration count\narg 3 : first client path (optional)\narg 4 : second "
        "client path (optional) "
    ))

elif len(sys.argv)>2:
    if os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1]):
        SERVER_PATH = sys.argv[1]
    else:
        panic("Invalid file path!")

    if sys.argv[2].isnumeric():
        num = int(sys.argv[2])
        if not 10 <= num <= 1000:
            panic("Second argument must be between 10 and 1000")
        else:
            SERVER_MAX_RUN_COUNT = num
    else:
        panic("Second argument must be a number!")

if len(sys.argv)==5:
    if os.path.exists(sys.argv[3]) and os.path.isfile(sys.argv[3]):
        CLIENT_1_PATH = sys.argv[3]
    else:
        panic("Invalid file path!")

    if os.path.exists(sys.argv[4]) and os.path.isfile(sys.argv[4]):
        CLIENT_2_PATH = sys.argv[4]
    else:
        panic("Invalid file path!")


LOGS_DIRECTORY_PATH:str = "./logs"

ANALYZE_LOG_PATH:str = "./result.log"


server_run_counter:int = 0

checked_logs:list = []


result_list:list = []


def get_options_input(input_message:str,options:list) -> str:
    if len(options)==0:
        panic("The length of the options list cannot be empty!")

    text:str = ""
    while True:
        text = input(input_message + " " + str(options)+" : ")
        if text in options:
            return text


def clean() -> int:
    if not os.path.exists(LOGS_DIRECTORY_PATH):
        return 0

    if get_options_input("Am I allowed to delete the log folder at \""+LOGS_DIRECTORY_PATH+"\"",
                         ["y","n"])=="n":
        panic("User did not give me the permission to delete a folder")

    try:
        shutil.rmtree(pathlib.Path(LOGS_DIRECTORY_PATH).absolute())
        return 0
    except OSError:
        return 1



def live_analyze_log_file():
    if os.path.exists(ANALYZE_LOG_PATH): os.remove(ANALYZE_LOG_PATH)
    bigString:str = ""

    dirty_trick:list=[]
    team_1_win_count:int = 1
    team_2_win_count:int = 1

    totalRunTime:float = 0
    for i in result_list:
        if i[1][0] not in dirty_trick:
            dirty_trick.append(i[1][0])
        else:
            if len(dirty_trick)==1:
                team_1_win_count+=1
            else:
                if i[1][0]==dirty_trick[0]:
                    team_1_win_count+=1
                else:
                    team_2_win_count+=1


        totalRunTime+=i[2]
        bigString+="server run count : "+str(i[0])+" , "+str(i[1]).center(35) +" run_time:"+str(
                        round(i[2],2))+"\n"


    if len(dirty_trick)==2:
        bigString+="\n"+("total games count : "+str(team_1_win_count+team_2_win_count)+"\n"

        )+dirty_trick[0]+" win count : "+str(team_1_win_count)+"\n"+dirty_trick[1]+" win count : "+(
                                str(team_2_win_count))+"\n total run time : "+str(round(totalRunTime,3))
    elif len(dirty_trick)==1:
        bigString += "\n" + ("total games count : " + str(team_1_win_count + team_2_win_count) + "\n"

                             ) + dirty_trick[0] + " win count : " + str(team_1_win_count) + "\n" + dirty_trick[
                         0] + "'s opponent win count : " + (
                         str(team_2_win_count)) + "\n total run time : " + str(round(totalRunTime, 3))




    o = open(ANALYZE_LOG_PATH,'a+')
    o.write(bigString)



def run_server() -> tuple[int,float]:
    t1:float = time.time()

    try:
        if server_run_counter==0:
            shutil.rmtree(pathlib.Path(CLIENT_LOG_PATH).absolute())

    except OSError as e:
        0

    # This is still error-prone, we don't know how the user runs python scripts

    result_code = subprocess.call("python3 "+SERVER_PATH+" -p1 "+CLIENT_1_PATH+" -p2 "+
                                  CLIENT_2_PATH , shell=True)
    if result_code!=0:
        result_code = subprocess.call("python " + SERVER_PATH + " -p1 " + CLIENT_1_PATH + " -p2 " +
                                      CLIENT_2_PATH, shell=True)
    if result_code!=0:
        result_code = subprocess.call("py " + SERVER_PATH + " -p1 " + CLIENT_1_PATH + " -p2 " +
                                      CLIENT_2_PATH, shell=True)

    try:
        newPath = CLIENT_LOG_PATH + "/" + str(server_run_counter)
        os.mkdir(pathlib.Path(newPath).absolute())
        target0 = pathlib.Path(CLIENT_LOG_PATH+"/AGENT0.log").absolute()
        target1 = pathlib.Path(CLIENT_LOG_PATH+"/AGENT1.log").absolute()
        target2 = pathlib.Path(CLIENT_LOG_PATH + "/AGENT2.log").absolute()
        target3 = pathlib.Path(CLIENT_LOG_PATH + "/AGENT3.log").absolute()


        dst0 = pathlib.Path(newPath + "/AGENT0.log").absolute()
        dst1 = pathlib.Path(newPath + "/AGENT1.log").absolute()

        shutil.move(target0,dst0)
        shutil.move(target1,dst1)
        os.remove(target2)
        os.remove(target3)

    except OSError as e:
        0

    t2:float = time.time()
    return result_code,t2-t1

def get_latest_log_path() -> tuple[str,str]:
    log_list = os.listdir(LOGS_DIRECTORY_PATH)

    for i in log_list:
        if i not in checked_logs:
            checked_logs.append(i)
            checked_logs.append(str(server_run_counter))
            return i, LOGS_DIRECTORY_PATH + "/" + i + "/game.json"

    panic("Could not find any new logs!")

def rename_log(log_path:str) -> int:
    global server_run_counter

    from_path = pathlib.Path(LOGS_DIRECTORY_PATH+"/"+log_path).absolute()
    to_path = pathlib.Path(LOGS_DIRECTORY_PATH+"/"+str(server_run_counter)).absolute()

    try:
        shutil.move(from_path,to_path)
        server_run_counter+=1
        return 0
    except OSError:
        return 1




def run_server_loop() -> None:
    server_run_time:float = 0
    for i in range(0,SERVER_MAX_RUN_COUNT):

        server_run_time = run_server()[1]
        log_path = get_latest_log_path()
        brief_report = get_brief_report(log_path[1])
        report_result:str = "server run count : "+str(i)+" , "+str(brief_report).center(35) +" run_time:"+str(
                        round(server_run_time,2))
        print(report_result)
        result_list.append(
            (
            i,
            brief_report,
            server_run_time
            )
        )

        rename_log(log_path[0])
        live_analyze_log_file()


def get_brief_report(target:str) -> tuple[str,str]:

    if not os.path.exists(target): panic("Target at \""+target+"\" does not exist!")

    target_dict = json.loads(open(target).read())
    winner:str = "undefined";win_reason:str = "undefined"
    target_dict_igd = target_dict["initial_game_data"]

    for i in target_dict_igd:
        if i == "winner": winner = target_dict_igd[i]
        elif i == "win_reason": win_reason = target_dict_igd[i]

    return winner,win_reason


def main() -> None:
    clean()
    run_server_loop()
    print("\nServer run iteration is over, check the log file at : \""+ANALYZE_LOG_PATH+"\"")



if __name__=="__main__":
    main()
