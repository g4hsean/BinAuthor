#include <vector>
#include <list>
#include <map>
#include <set>
#include <deque>
#include <stack>
#include <bitset>
#include <algorithm>
#include <functional>
#include <numeric>
#include <utility>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <ctime>

using namespace std;

int main() {
  freopen("in", "r", stdin);
  freopen("out", "w", stdout);
  int tt;
  scanf("%d", &tt);
  for (int qq=1;qq<=tt;qq++) {
    printf("Case #%d: ", qq);
    bool can[42];
    for (int i = 1; i <= 16; i++) can[i] = true;
    for (int q = 0; q < 2; q++) {
      int row;
      scanf("%d", &row);
      for (int i = 1; i <= 4; i++)
        for (int j = 1; j <= 4; j++) {
          int a;
          scanf("%d", &a);
          if (i != row) can[a] = false;
        }
    }
    int res = -1;
    for (int i = 1; i <= 16; i++)
      if (can[i]) {
        if (res != -1) {
          res = -2;
          break;
        }
        res = i;
      }
    if (res == -1) puts("Volunteer cheated!"); else
    if (res == -2) puts("Bad magician!");
    else printf("%d\n", res);
  }
  return 0;
}
