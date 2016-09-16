#include<stdio.h>
#include<stdlib.h>
int main(){
    int n=4;
    int cas, c1, c2, m1[4], m2[4];
    scanf("%d", &cas);
    for (int ii=0; ii<cas; ii++) {
        scanf("%d", &c1);
        for (int i=0; i<4; i++) {
            for (int j=0; j<4; j++){
                if (i+1 != c1) scanf("%*d");
                else scanf("%d", &m1[j]);
            }
        }
        scanf("%d", &c2);

        for (int i=0; i<4; i++) {
            for (int j=0; j<4; j++){
                if (i+1 != c2) scanf("%*d");
                else scanf("%d", &m2[j]);
            }
        }
        int ans = -1;
        for (int i=0; i<4; i++) {
            for (int j=0; j<4; j++) {
                if (m1[i] == m2[j]) {
                    if (ans == -1) ans = m1[i];
                    else ans = -2;
                }
            }
        }
        if (ans >= 0) printf("Case #%d: %d\n", ii+1, ans);
        else printf("Case #%d: %s\n", ii+1, ans == -1 ? "Volunteer cheated!" : "Bad magician!");
    }
    return 0;
}
