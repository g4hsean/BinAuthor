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

vector <string> solve(int r, int c, int m) {
  string w = "";
  for (int j = 0; j < c; j++) w += ".";
  vector <string> ret;
  for (int i = 0; i < r; i++) ret.push_back(w);
  if (m == 0) {
    ret[0][0] = 'c';
    return ret;
  }
  if (m == r * c - 1) {
    for (int i = 0; i < r; i++)
      for (int j = 0; j < c; j++) ret[i][j] = '*';
    ret[0][0] = 'c';
    return ret;
  }
  if (r == 1) {
    for (int j = 0; j < m; j++) ret[0][j] = '*';
    ret[0][c - 1] = 'c';
    return ret;
  }
  if (m >= r * c - 3) {
    return vector <string>();
  }
  if (r == 2) {
    if (m % 2 == 1) {
      return vector <string>();
    }
    for (int i = 0; i < 2; i++)
      for (int j = 0; j < m / 2; j++) ret[i][j] = '*';
    ret[0][c - 1] = 'c';
    return ret;
  }
  for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++) ret[i][j] = '*';
  m = r * c - m;
  if (m == 5 || m == 7) {
    return vector <string>();
  }
  if (m == 2 * r + 1) {
    for (int i = 0; i < r - 1; i++)
      for (int j = 0; j < m / r; j++) ret[i][j] = '.';
    ret[0][m / r] = '.';
    ret[1][m / r] = '.';
    ret[2][m / r] = '.';
    ret[0][0] = 'c';
    return ret;
  }
  if (m >= 2 * r) {
    for (int i = 0; i < r; i++)
      for (int j = 0; j < m / r; j++) ret[i][j] = '.';
    for (int i = 0; i < m % r; i++) ret[i][m / r] = '.';
    if (m % r == 1) {
      ret[1][m / r] = '.';
      ret[r - 1][m / r - 1] = '*';
    }
    ret[0][0] = 'c';
    return ret;
  }
  if (m % 2 == 0) {
    for (int i = 0; i < m / 2; i++)
      for (int j = 0; j < 2; j++) ret[i][j] = '.';
    ret[0][0] = 'c';
    return ret;
  }
  for (int i = 0; i < (m - 3) / 2; i++)
    for (int j = 0; j < 2; j++) ret[i][j] = '.';
  ret[0][2] = '.';
  ret[1][2] = '.';
  ret[2][2] = '.';
  ret[0][0] = 'c';
  return ret;
}

int main() {
  freopen("in", "r", stdin);
  freopen("out", "w", stdout);
  freopen("log", "w", stderr);
  int tt;
  scanf("%d", &tt);
  for (int qq=1;qq<=tt;qq++) {
    printf("Case #%d:\n", qq);
    int r, c, m;
    scanf("%d %d %d", &r, &c, &m);
    vector <string> ret;
    if (r <= c) {
      ret = solve(r, c, m);
    } else {
      vector <string> temp = solve(c, r, m);
      if (!temp.empty()) {
        for (int i = 0; i < r; i++) {
          string w = "";
          for (int j = 0; j < c; j++) w += temp[j][i];
          ret.push_back(w);
        }
      }
    }
    if (ret.empty()) {
      puts("Impossible");
    } else {
      int cs = 0, cc = 0;
      for (int i = 0; i < r; i++)
        for (int j = 0; j < c; j++)
          if (ret[i][j] == 'c') cc++; else
          if (ret[i][j] == '*') cs++;
      if (cc != 1 || cs != m) {
        cerr << "ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! at test " << qq << ": " << r << " " << c << " " << m << endl;
      }
      for (int i = 0; i < r; i++) printf("%s\n", ret[i].c_str());
    }
  }
  return 0;
}
