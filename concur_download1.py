import concurrent.futures
import urllib.request
import re
import threading
import time
import urllib.request
from multiprocessing import Pool


LINKS = ["http://music.lib.ru/janr/index_janr_10-1.shtml",
         #"http://podgames.ogl.ru/",
         "http://doctor.podfm.ru/rss/rss.xml",
         "http://www.neizvestniy-geniy.ru/cat/music/podari_mne_nadezdu/"
         
         
]

def find_mp3_links(main_url):
    data = str(urllib.request.urlopen(main_url).read())
    #print(data)
    #Searching absolute references:
    mp3_links = re.findall('http:[a-zA-Z0-9\./_-]*?\.mp3', data)
    #Searching relative references:
    try:
        serv_name = re.findall('http://[a-zA-Z0-9\._-]*', main_url)[0]
        relative_part_list = re.findall('/[a-zA-Z0-9\./_-]*?\.mp3', data)
        mp3_links += [serv_name + r for r in relative_part_list]
    except:
        pass
    #print("\n".join(mp3_links))
    return mp3_links

def save_file(link):
    try:
        mp3file = urllib.request.urlopen(link)
    except:
        return 'u-'
    output = open(link.split('/')[-1], 'wb')
    try:
        #print("s")
        data = mp3file.read()
        output.write(data)
        output.close()
        #print("f")
        return 'w+'
    except:
        output.close()
        return 'r-'
    
    
#========= Serial execution: ======
def serial_exec(list_of_links):
    start_time = time.time()
    num = 1
    for i in list_of_links:
        print (num, ": ", save_file(i), time.time() - start_time, sep=' ')
        #save_file(i)
        num += 1

#===== Threading: ==================
# http://stackoverflow.com/questions/18883964/asynchronous-file-downloads-in-python
# http://stackoverflow.com/questions/13481276/threading-in-python-using-queue/13481586#13481586
class DownloadThread(threading.Thread):
    def __init__(self, link):
        threading.Thread.__init__(self)
        self.link = link
    
    def run(self):
        save_file(self.link)

        
def threading_func(list_of_links):
    for i in range(len(list_of_links)):
        tmp = list_of_links[i]
        t = DownloadThread(tmp)
        t.setDaemon(True)
        t.start()
        t.join()

        
#===== Multiprocessoring ===========
def multiprocess_func(list_of_links, number_of_workers):
    with Pool(processes=number_of_workers) as pool:
        pool.map(save_file, list_of_links)


#===== Concurrent.futures (Python 3.2+): ============
# https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
def concurrent_futures(list_of_links, number_of_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        results = {executor.submit(save_file, link): link for link in list_of_links}
        completed = concurrent.futures.as_completed(results)
        #print("concurrent.futures: ", dir(concurrent.futures))
        #print(completed, "\ntype: ", type(completed))
    

if __name__ == '__main__':
    print("Choose test mp3 files:\n",
          "0 - songs( 2-6Mb each file, max number = 10 files)\n",
          "1 - podcasts (~40Mb each file, Webserver returns in one thread.)\n",
          "2 - songs( 4-10Mb each file, max number = 30 )\n",
          "")
    test_number = int(input("Test suite:"))
    list_of_links = find_mp3_links(LINKS[test_number])
    print("\n 9 - Show available links\n",
          "0 - Serial implementation\n",
          "1 - Threading (number of threads = number of links)\n",
          "2 - Multiprocessing\n",
          "3 - Concurrent_futures (ThreadPool-, ProcessPoolExecutor)\n",
          #"4 - Non-blocking IO and Event loop\n",
          #"5 - Asyncio"
          )
    ch = int(input("Make your choice: "))
    
    # If we begin to get mp3 files (ch<>9), we determine the number of them,
    # and then reduce the length of list with test links:
    if ch != 9:
        number_of_files = int(input("Number of files for downloading" +
                                    "(no more than " + 
                                    str(len(list_of_links)) + "):"))
        list_of_links = list_of_links[0:number_of_files]
        # print("LoL:", list_of_links)
    if ch in (2, 3):
        number_of_items = int(input("Give number of items: "))
        
    start_time = time.time()
    if ch == 9:
        print("Mp3 links:\n:", ("\n").join(list_of_links))
        print("Mp3 amount:", len(list_of_links))
    elif ch == 0:
        serial_exec(list_of_links)
    elif ch == 1:
        threading_func(list_of_links)
    elif ch == 2:
        multiprocess_func(list_of_links, number_of_items)
    elif ch == 3:
        concurrent_futures(list_of_links, number_of_items)
    else:
        raise NotImplementedError
        
    if ch != 9:
        print("\nMethod of exec.:" , ch, "\nTime: ", time.time() - start_time)
    
# ===========================================================   
# Results:

# Serial: 
    # files: 10-71 (60 files) 85.21sec - in one thread

# Concurrent_features:
    # Result: Devzen - 157.93 sec (7 files, 7 workers), ~446Mb
    # list_of_links[10:71] - 60 files, 10 threads, 62,60sec
    # list_of_links[10:71] - 60 files, 20 threads, 52,70sec
    # list_of_links[10:71] - 60 files, 30 threads, 57,29sec

