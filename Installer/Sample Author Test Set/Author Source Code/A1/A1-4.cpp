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

pair <double, int> a[123456];

int main() {
  freopen("in", "r", stdin);
  freopen("out", "w", stdout);
  int tt;
  scanf("%d", &tt);
  for (int qq=1;qq<=tt;qq++) {
    printf("Case #%d: ", qq);
    int n;
    cin >> n;
    for (int i = 0; i < n; i++) {
      cin >> a[i].first;
      a[i].second = 1;
    }
    for (int i = 0; i < n; i++) {
      cin >> a[i + n].first;
      a[i + n].second = -1;
    }
    sort(a, a + n + n);
    int z = 0, cz = 0;
    for (int i = n + n - 1; i >= 0; i--) {
      cz += a[i].second;
      if (cz > z) z = cz;
    }
    int y = 0, bal = 0;
    for (int i = n + n - 1; i >= 0; i--) {
      if (a[i].second == 1) {
        bal++;
      } else {
        if (bal > 0) {
          bal--;
          y++;
        }
      }
    }
    printf("%d %d\n", y, z);
  }
  return 0;
}
