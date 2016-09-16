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
    double c, f, x;
    cin >> c >> f >> x;
    double spent = 0, ans = 1e30;
    int km = -1;
    double rate = 2.0;
    for (int farms = 0; farms <= 1000000; farms++) {
      double current = spent + x / rate;
      if (current < ans) {
        ans = current;
        km = farms;
      }
      spent += c / rate;
      rate += f;
    }
    printf("%.7lf\n", ans);
    cerr << "at " << km << endl;
  }
  return 0;
}
