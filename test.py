class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def f(p,p0,pm,d):
    return max(p0,(p-d)+min(0,pm-(p+d))),min(pm,(p+d)+max(0,p0-(p-d)))

p0 = 1
pm = 10
d = 2

print "p0",p0,"pm",pm
for p in range(p0,pm+1):
    r = f(p,p0,pm,d)
    for i in range(r[0],r[1]+1):
        if i == p:
            print color.GREEN + str(i) + color.END,
        else:
            print i,
    print


Rise up like the yeast 
Run free like the beast 
Sail full like the wind 
Eat as if with best of friends 
Fall yes 
Hate no 
Dream your dreams 
Shovel snow 
Rise up, you are BIG 
Scratchy branch becomes a twig 
Reach high 
Fall low 
Dream yes 
Hate no 
Run free, let legs roam 
Full sail brings you home. 

#letyourlightshine
