
#include <stdio.h>

int g_a;
int g_arr[2] = {1, 2};
int* g_p;

int hoge(int i)
{
	int i = 0;
	printf("%d\n", i);
	return 0;
}

int main(int argc, char* argv[])
{
	printf("%p\n", main);
	int hoge;
	int main = 0;
	main = 1000;
	printf("%d\n", main);
	for (int i=0; i<5; ++i) {
		if (i == 2) {
			hoge = 10;
		}
	}
	return 0;
	for (int i=0; i<5; ++i) {
		for (int j=0; j<5; ++j) {
			if (i == 3) {
				break;
			}
			{
				continue;
			}
			++i;
		}
		printf("%d\n", i);
	}
	return 0;
}

