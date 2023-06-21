import time

class TimeUtils():
    def getDifferenceFromCurrentTime(comparisionTime):
        currentTime = time.perf_counter()
        
        return (currentTime - comparisionTime)