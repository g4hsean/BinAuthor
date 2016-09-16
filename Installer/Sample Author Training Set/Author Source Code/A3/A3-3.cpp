#include <algorithm>
#include <string>
#include <vector>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
//#include <iostream>
#include <set>
//#include <map>
//#include <sstream>

using namespace std;

typedef long long ll;
typedef long double ld;
typedef vector<int> vi;
typedef vector<int> vll;
typedef vector<string> vs;

int err;

#define LS <
#define Size(x) (int(x.size()))
#define LET(k,val) typeof(val) k = (val)
#define CLC(act,val) (*({act; static typeof(val) CLCR; CLCR = (val); &CLCR;}))

#define FOR(k,a,b) for(typeof(a) k=(a); k LS (b); ++k)
#define FORREV(k,a,b) for(typeof(b) k=(b); (a) <= (--k);)

#define FIRST(k,a,b,cond) CLC(LET(k, a); for(; k LS (b); ++k) if(cond) break, k)
#define LAST(k,a,b,cond) CLC(LET(k, b); while((a) <= (--k)) if(cond) break, k)
#define EXISTS(k,a,b,cond) (FIRST(k,a,b,cond) LS (b))
#define FORALL(k,a,b,cond) (!EXISTS(k,a,b,!(cond)))
#define FOLD0(k,a,b,init,act) CLC(LET(k, a); LET(R##k, init); for(; k LS (b); ++k) {act;}, R##k)
#define SUMTO(k,a,b,init,x)  FOLD0(k,a,b,init,R##k += (x))
#define SUM(k,a,b,x) SUMTO(k,a,b,(typeof(x)) (0), x)
#define PRODTO(k,a,b,init,x) FOLD0(k,a,b,init,R##k *= (x))
#define PROD(k,a,b,x) PRODTO(k,a,b,(typeof(x)) (1), x)
#define MAXTO(k,a,b,init,x)  FOLD0(k,a,b,init,R##k >?= (x))
#define MINTO(k,a,b,init,x)  FOLD0(k,a,b,init,R##k <?= (x))
#define QXOR(k,a,b,x) FOLD0(k,a,b,(typeof(x)) (0), R##k ^= x)
#define QAND(k,a,b,x) FOLD0(k,a,b,(typeof(x)) (-1), R##k &= x)
#define QOR(k,a,b,x) FOLD0(k,a,b,(typeof(x)) (-1), R##k |= x)
#define FOLD1(k,a,b,init,act) CLC(LET(k, a); LET(R##k, init); for(++k; k LS (b); ++k) act, R##k)
#define MAX(k,a,b,x) FOLD1(k,a,b,x, R##k >?= (x))
#define MIN(k,a,b,x) FOLD1(k,a,b,x, R##k <?= (x))
#define FIRSTMIN(k,a,b,x) (MIN(k,a,b,make_pair(x,k)).second)

int bitc(ll r) {return r == 0 ? 0 : (bitc(r>>1) + (r&1));}
ll gcd(ll x, ll y) {return x ? gcd(y%x,x) : y;}

// template<class T> T& operator >?= (T& x, T y) {if(y>x) x=y; return x;}
// template<class T> T& operator <?= (T& x, T y) {if(y<x) x=y; return x;}
// template<class T> T operator >? (T x, T y) {return x>y?x:y;}
// template<class T> T operator <? (T x, T y) {return x<y?x:y;}

#define Pa(xy) ((xy).first)
#define Ir(xy) ((xy).second)

string cts(char c) {string s=""; s+=c; return s;}

/// ----

#define BUFSIZE 1000000
char buf[BUFSIZE];

#ifdef DEBUG
#define DEB(x) x
#else
#define DEB(x)
#endif

string getLine() {
  string s;
  while(!feof(stdin)) {
    char c = fgetc(stdin);
    if(c == 13) continue;
    if(c == 10) return s;
    s += c;
    }
  return s;
  }

int getNum() {
  string s = getLine();
  return atoi(s.c_str());
  }

vi parsevi(string s) {
  s = s + " ";
  int q = 0;
  bool minus = false;
  vi res;
  FOR(l,0, Size(s)) {
    if(s[l] == ' ') { res.push_back(minus?-q:q); q = 0; minus = false;}
    else if(s[l] == '-') { minus = true; }
    else { q = q * 10 + s[l] - '0'; }
    }
  return res;
  }

int Tests, cnum;

//Eryx

// !FDI

void solveCase() {
  int R, C, M, F;
  
  err = scanf("%d%d%d", &R, &C, &M);
  
  int X = C, Y = R;
  
  F = R*C-M;
  
  printf("Case #%d: \n", cnum);

  if(C == 1) {
    FOR(y, 0, R) printf("%c\n", y==0 ? 'c' : y < F ? '.' : '*');
    }
  
  else if(R == 1) {
    FOR(y, 0, C) printf("%c", y==0 ? 'c' : y < F ? '.' : '*');
    printf("\n");
    }
  
  else if(F == 1) {
    FOR(y, 0, Y) {
      FOR(x, 0, X) printf("%c", y==0 && x==0 ? 'c' : '*');
      printf("\n");
      }
    }
  
  else if(C == 2 && !(M%2) && F >= 4) {
    C /= 2; F /= 2;
    FOR(y, 0, R) {
      char h = y==0 ? 'c' : y < F ? '.' : '*';
      char j = h == 'c' ? '.' : h;
      printf("%c%c\n", j, h);
      }
    }
  
  else if(R == 2 && !(M%2) && F >= 4) {
    R /= 2; F /= 2;
    FOR(t, 0, 2) {
      FOR(y, 0, C) {
        char h = y==0 && t == 0 ? 'c' : y < F ? '.' : '*';
        printf("%c", h);
        }
      printf("\n");
      }
    }
  
  else if(C == 2 || R == 2) {
    printf("Impossible\n");
    }
  
  else if(F == 4) {
    FOR(y, 0, Y) {
      FOR(x, 0, X) printf("%c", y==0 && x==0 ? 'c' : y<2&&x<2 ? '.' : '*');
      printf("\n");
      }
    }
  
  else if(F == 6) {
    FOR(y, 0, Y) {
      FOR(x, 0, X) printf("%c", y==1 && x==0 ? 'c' : y<3&&x<2 ? '.' : '*');
      printf("\n");
      }
    }
  
  else if(F < 8) {
    printf("Impossible\n");
    }
  
  else {
    char mmap[60][60];
    FOR(y,0,Y) FOR(x,0,X) mmap[y][x] = '*';
    FOR(y,0,Y) mmap[y][X] = 0;

    FOR(y,0,2) FOR(x,0,2) mmap[y][x] = '.';
    mmap[0][0] = 'c';
    F -= 4;
    
    int ly = 2;
    int lx = 2;
    
    mmap[0][lx] = mmap[1][lx] = '.';
     F -= 2; lx++;

    while(F >= 2 && ly < Y) {
      mmap[ly][0] = mmap[ly][1] = '.';
      F -= 2; ly++;
      }
    
    while(F >= 2 && lx < X) {
      mmap[0][lx] = mmap[1][lx] = '.';
      F -= 2; lx++;
      }
    
    FOR(y,0,ly) FOR(x,0,lx) if(mmap[y][x] == '*' && F) {
      F--; mmap[y][x] = '.';
      }

    if(F) printf("Impossible\n"); 
    else FOR(y,0,Y) printf("%s\n", mmap[y]);
    }
  
  }

int main() {

  if(0)
    Tests = 1;
  else if(1)
    err = scanf("%d", &Tests);
  else {
    string Nstr = getLine();
    Tests = atoi(Nstr.c_str());
    }
  
  for(cnum=1; cnum<=Tests; cnum++)
    solveCase();
    
  // finish
  return 0;
  }

// This solution includes hidden routines to solve test cases in separate
// processes in order to make it faster. I will update them to run on a
// cluster if I get one ;)
