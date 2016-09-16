#include<stdio.h>
#include<algorithm>
int main() {
    int cas, n, ans[2], r;
    double a[2][1010];
    scanf("%d", &cas);
    for (int ii=0; ii<cas; ii++) {
        scanf("%d", &n);
        for(int i=0; i<2; i++) {
            for(int j=0; j<n; j++) {
                scanf("%lf", &a[i][j]);
            }
        }
        std::sort(a[0], a[0]+n);
        std::sort(a[1], a[1]+n);
        for(int i=0; i<2; i++) {
            r = 0;
            for (ans[i]=0; ans[i]<n; ans[i]++, r++) {
                while(a[i][ans[i]]>a[1-i][r] && r < n)r++;
                if (r == n)break;
            }
        }
        printf("Case #%d: %d %d\n", ii+1, ans[1], n-ans[0]);
    }
    return 0;
}