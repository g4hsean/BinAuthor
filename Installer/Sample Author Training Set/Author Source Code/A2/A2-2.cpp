#include <stdio.h>
int main() {
    int cas;
    scanf("%d", &cas);
    for (int ii=0; ii<cas; ii++) {
        double c, f, x, t=0.0, s=2.0;
        scanf("%lf%lf%lf", &c, &f, &x);
        while (s < f * x / c - f) {
            t += c / s;
            s += f;
        }
        t += x / s;
        printf ("Case #%d: %.7f\n", ii+1, t);
    }
    return 0;
}