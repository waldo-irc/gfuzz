#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse, httplib, sys, math, time
from sys import stdout
from time import sleep

#Here we begin parsing our arguments.
parser = argparse.ArgumentParser(description='Fuzz HTTP GET Request Vars.')
parser.add_argument('url', metavar='url', type=str, nargs='+', help='A url to fuzz.')
parser.add_argument('--wordlist=', type=str, help="Fuzz with a wordlist (required)", dest="wordlist", action="store", default=False)
parser.add_argument('-delay', type=float, help="Add a delay", dest="delay", action="store", default=False)
parser.add_argument('-p', help="Run with all possible permutations for 2 variable user brute force.", dest="perms", action="store_true", default=False)
parser.add_argument('-ssl', help="Run with ssl (http by default).", dest="ssl", action="store_true", default=False)

#Here we store some important variables, each has a pretty self explanatory varname
t0 = time.time() 
args = parser.parse_args()
url = args.url[0].split('?')[0].split('/')[0]
page = args.url[0].split('?')[0].split('/')[1]
try:
     argsplit = args.url[0].split('?')[1]
except IndexError:
     print '[!!] No vars in your GET request!'
     exit(0)
varargs = argsplit.split('&')
varis = []
brutelist = []

#Here we store our GET variables in a list
for line in varargs:
     newline = line.split('=')[0]
     varis.append(newline)

#And here we parse for errors.  A wordlist is required to fuzz the Variables and you must provide at least 1 variable that is being fuzzed or why run the script!
if args.wordlist is False:
     print "[!!] Error!  Must provide a wordlist."
     exit(0)

if "*" not in ''.join(varargs):
     print "[!!] Must provide a var to fuzz!"
     exit(0)

#This reads our wordlist and stores each word in a list - (brutelist = [] from above)
print "[*] Getting your wordlist ready, the bigger the list the longer this takes."
with open(args.wordlist, 'r') as wordlist:
     for line in wordlist:
          brutelist.append(line.split('\n')[0])

#Just some confirmation prompts to make sute you got the right URL and arguments.
print '[*] Variables to fuzz are... ' + ' '.join(varis)

print '[*] Url to fuzz is %s.' % url

userinput = raw_input('[*] Continue? y/N?: ')
if userinput.lower() != 'y':
     print '[*] Exiting!'
     exit(0)

#This opens our http/https connection
if args.ssl is False:
     conn = httplib.HTTPConnection("%s" % url)
else:
     conn = httplib.HTTPSConnection("%s" % url)      

print '[*] List is %s words long.  Get ready!' % len(brutelist)

#This runs if we DONT use the -p parameter.  it's a standard fuzz of all provided variables with a wordlist.
if args.perms is False:
     varamt = len(varis)
     fullprog = float(100) / len(brutelist)
     progression = float(0)

     for line in brutelist:
          tmp = ''
          tmp2 = 1
          t1 = time.time()
          total = str(t1-t0).split('.')[0]
          progression+=fullprog

          for varrr in varargs:
               varr = varrr.split('=')[1]
               fuzzvar = varrr.split('=')[0]
               if varr == '*':
                    if varamt == tmp2:
                         tmp+=fuzzvar + '=%s' % line
                    else:
                         tmp+=fuzzvar + '=%s&' % line
                         tmp2+=1
               else:
                    if varamt == tmp2:
                         tmp+=fuzzvar + '=%s' % varr
                    else:
                         tmp+=fuzzvar + '=%s&' % varr
                         tmp2+=1

          if page == "":
                finalvar = '?' + tmp
          else:
                finalvar = page + '?' + tmp

          conn.request("GET", "/%s" % finalvar)
          resp = conn.getresponse()
          response = "%s %s" % (resp.status, resp.reason)
          sys.stdout.write('\x1b[2K')
          stdout.write('\rTime elapsed: %s seconds, Progress:(%s%%)[%s]' % (total,str(progression).split('.')[0],finalvar))
          stdout.flush()
          with open('./fuzzlog.txt', 'a+') as myfile:
               myfile.write("http(s)://%s/%s\n" % (url, finalvar))
               myfile.write('%s \n' % response)
               myfile.write('%s \n' % resp.read())
          if args.delay is not False:
               sleep(args.delay)

#This runs if we do a -p parameter.  It takes the first variable and runs all permutations of the wordlist against it and a second variable.  
if args.perms is not False:

     xy = 0
     xyz = 0
     for variables in varargs:
          if variables.split('=')[1] == '*':
               xy+=1

     varamt = len(varis)
     fullprog = float(100) / (math.pow(len(brutelist), 2)) #Here we set up the new % bar.  This solution was simple, We go through each line in the brutelist brutelist amount of times, IE brutelist squared.
     progression = float(0) #This was my simple solution to making it hit 100% everytime.  If it's a float point then it's way more accurate.  

     #These are some nested loops required to do the permutations properly.  for each line in the brutelist it runs everyline in the brutelist against it.
     for currarg in varargs:
          if currarg.split('=')[1] != '*':
               continue
          else:
               pass

          if xyz >= 1: #Here we make it so only the first paramater fuzzes through, no more repition.
               continue

          xyz+=1

          currentarg = currarg.split('=')[0]

          for lines in brutelist:
               currline = lines

               for line in brutelist:
                    tmp = ''
                    tmp2 = 1
                    t1 = time.time()
                    total = str(t1-t0).split('.')[0]
                    progression+=fullprog

                    for varrr in varargs:
                         varr = varrr.split('=')[1]
                         fuzzvar = varrr.split('=')[0]
                         if fuzzvar == currentarg: #This one is necessary so that our current 'username' parameter properly gets fuzzed against every iteration of the wordlist.
                              if varamt == tmp2:
                                   tmp+=fuzzvar + '=%s' % currline
                              else:
                                   tmp+=fuzzvar + '=%s&' % currline
                                   tmp2+=1
                         elif varr == '*':
                              if varamt == tmp2:
                                   tmp+=fuzzvar + '=%s' % line
                              else:
                                   tmp+=fuzzvar + '=%s&' % line
                                   tmp2+=1
                         else:
                              if varamt == tmp2:
                                   tmp+=fuzzvar + '=%s' % varr
                              else:
                                   tmp+=fuzzvar + '=%s&' % varr
                                   tmp2+=1

                    if page == "":
                         finalvar = '?' + tmp
                    else:
                         finalvar = page + '?' + tmp

                    conn.request("GET", "/%s" % finalvar)
                    resp = conn.getresponse()
                    response = "%s %s" % (resp.status, resp.reason)
                    sys.stdout.write('\x1b[2K')
                    stdout.write('\rTime elapsed: %s seconds, Progress:(%s%%)[%s]' % (total,str(progression).split('.')[0],finalvar))
                    stdout.flush()
                    with open('./fuzzlog.txt', 'a+') as myfile:
                         myfile.write("http(s)://%s/%s\n" % (url, finalvar))
                         myfile.write('%s \n' % (response))
                         myfile.write('%s \n' % resp.read())
                    if args.delay is not False:
                         sleep(args.delay)

stdout.write("\n")
print "[*] Finished!  Check fuzzlog.txt for output"
