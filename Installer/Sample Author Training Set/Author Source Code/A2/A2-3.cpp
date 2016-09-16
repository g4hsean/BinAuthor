#include<stdio.h>
#include<stdlib.h>
#include<string.h>
char ans[55][55];
int main() {
    int cas, r, c, m, pos, v;
    scanf("%d", &cas);
    for (int ii=0; ii<cas; ii++) {
        scanf("%d%d%d", &r, &c, &m);
        memset(ans, 0, sizeof(ans));
        pos = 1;
        if (r == 1) {
            for(int i=0;i<m;i++)ans[0][i]='*';
            for(int i=m;i<c;i++)ans[0][i]='.';
            ans[0][c-1] = 'c';
        } else if (c==1) {
            for(int i=0;i<m;i++)ans[i][0]='*';
            for(int i=m;i<r;i++)ans[i][0]='.';
            ans[r-1][0] = 'c';
        } else if (m == r * c - 1) {
            for(int i=0; i<r; i++) for(int j=0; j<c; j++)ans[i][j] = i==0&&j==0?'c':'*';
        } else if (r == 2) {
            if (r*c-m == 2 || m%2!=0) pos = 0;
            else{
                for(int i=0; i<r; i++) for(int j=0; j<c; j++)ans[i][j] = j<m/2?'*':'.';
                ans[0][c-1] = 'c';
            }
        } else if (c == 2) {
            if (r*c-m == 2 || m%2!=0) pos = 0;
            else {
                for(int i=0; i<r; i++) for(int j=0; j<c; j++)ans[i][j] = i<m/2?'*':'.';
                ans[r-1][0] = 'c';
            }
        } else {
            v = r*c - m;
            if (v == 2 || v == 3 || v == 5 || v == 7) pos = 0;
            else{
                if (v / c <= 2) {
                    for(int i=0; i<r; i++) for(int j=0; j<c; j++)
                        ans[i][j] = i<3 && j*3+i<v?'.':'*';
                    if (v%3 == 1) {ans[1][v/3] = '.'; ans[2][v/3-1] = '*';}
                    ans[0][0] = 'c';
                } else {
                    for(int i=0; i<r; i++) for(int j=0; j<c; j++)
                        ans[i][j] = i*c+j<v?'.':'*';
                    if (v % c == 1) {
                        ans[v/c][1] = '.'; ans[v/c-1][c-1] = '*';
                    }
                    ans[0][0] = 'c';
                }
            }
        }
        if (pos) {
            printf("Case #%d:\n", ii+1);
            for(int i=0; i<r; i++) puts(ans[i]);
        } else {
            printf("Case #%d:\nImpossible\n", ii+1);

        }
    }
    return 0;
}