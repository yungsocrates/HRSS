def runner_up(arr):
    ls = list(arr)
    first = max(ls)
    ls2 = [x for x in ls if x != first]
    runner_up = max(ls2)

    print(runner_up)


if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())
    runner_up(arr)