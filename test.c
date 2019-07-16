#include <gmp.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    mpz_t n, n2;
    mpz_init2(n, 10);
    mpz_init2(n2, 10);
    mpz_setbit(n, 2);

    mpz_com(n2, n);

    mpz_out_str(stdout, 2, n2);
    printf("\n");

    mpz_clear(n);
    mpz_clear(n2);
    
    return 0;
}
