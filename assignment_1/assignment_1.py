flag = 0
i = 0
ctr = 'A'

def stringToInt(num) :
    try:
        int(num)
    except:
        global flag
        flag += 1
        print("리스트에 올바른 값을 기입해주세요")
        #예외처리

def error() :
    global flag
    flag += 1
    print("올바른 값을 기입해주세요")

def swap(A, B, list) :
     list[A],list[B] = list[B],list[A]

def AscendingPartition(first, last, list) :
    pibut = list[last]
    pibutPosition = last # 처음 피벗의 인덱스
    last -= 1
    while first <= last :

        while first <= last and list[first] <= pibut :
            first += 1
        while first <= last and list[last] >= pibut :
            last -= 1
        if first <= last :
            swap(first,last,list)

    swap(first,pibutPosition,list)

    return first

def DescendingPartition(first, last, list) :
    pibut = list[last]
    pibutPosition = last # 처음 피벗의 인덱스
    last -= 1
    while first <= last :

        while first <= last and list[first] >= pibut:
            first += 1
        while first <= last and list[last] <= pibut:
            last -= 1
        if first <= last :
            swap(first,last,list)

    swap(first,pibutPosition,list)
        
    return first
    
def quicksort(first,last,list,order) :
    
    if  ( first > 14 or first < 0 or last > 14 or last < 0 or first > last ) :
        return    # 예외처리 : 잘못된 범위
    if order == "A" :
        index = AscendingPartition(first,last,list)
    elif order == "D" :
        index = DescendingPartition(first,last,list)
    
    quicksort(first,index-1,list,order)
    quicksort(index+1,last,list,order)



arr=list() # 정렬할 리스트
string = input().split() # 입력을 받음



while i+1 :
    if string[i] == "-o" : # -o 일경우 다음으로 A 또는 D가 나와야 함
        i += 1
        if(string[i] == "A" or string[i] == "D") :
            ctr = string[i]
        else :
            error()
            break
        i += 1
    elif string[i] == "-i" : # -i 일경우 다음으로 정수가 나와야 함
        i += 1
        
        for j in range(i,len(string)) :
            stringToInt(string[j]) # 예외경우를 판별
            if flag >= 1 :
                break
            arr.append( int( string[j] ) )
        break
    else :
        error()
        break  # 예외처리
if flag == 0 :
    quicksort(0,len(arr)-1,arr,ctr)
    print(arr)
