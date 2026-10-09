# Практическое занятие №1. Основы работы в командной строке Linux

## Задача 1

```bash
sort /etc/passwd | grep -o '^[^:]*'
```

## Задача 2

```bash
awk '{print $2, $1}' /etc/protocols | tail -5 | sort -r
```

## Задача 3

```bash
#!/usr/bin/env bash

text=$1
printf -v border '%*s' "$((${#text} + 2))" ''
border=${border// /-}
printf '+%s+\n| %s |\n+%s+\n' "$border" "$text" "$border"
```

```bash
chmod +x banner
```

```bash
shellcheck banner
```

## Задача 4

```bash
#!/usr/bin/env bash

grep -oE '[A-Za-z_][A-Za-z0-9_]*' "$1" | sort -u | paste -sd ' ' -
```

```bash
chmod +x identifiers
```

## Задача 5

```bash
#!/usr/bin/env bash

chmod 755 "$1"
sudo cp "$1" /usr/local/bin/
```

```bash
chmod +x reg
```

## Задача 6

```bash
#!/usr/bin/env bash
directory=${1:-.}

for file in "$directory"/*.{c,js,py}; do
    [ -f "$file" ] || continue
    case $file in
        *.py) regex='^[[:space:]]*#' ;;
        *)    regex='^[[:space:]]*(//|/\*)' ;;
    esac

    if head -n 1 "$file" | grep -Eq "$regex"; then
        echo "$(basename "$file"): comment found"
    else
        echo "$(basename "$file"): no comment"
    fi
done
```

```bash
chmod +x check_comments
```

## Задача 7

```bash
#!/usr/bin/env bash

find "$1" -type f -exec sha256sum {} + | sort | uniq -w 64 -D | cut -d' ' -f3-
```

```bash
chmod +x duplicates
```

## Задача 8

```bash
#!/usr/bin/env bash

tar -cf "archive_$2.tar" -- "$1"/*."$2"
```

```bash
chmod +x archive_ext
```

## Задача 9

```bash
#!/usr/bin/env bash

sed 's/    /\t/g' "$1" > "$2"
```

```bash
chmod +x spaces_to_tabs
```

## Задача 10

```bash
#!/usr/bin/env bash

find "$1" -maxdepth 1 -type f -name '*.txt' -empty -printf '%f\n'
```

```bash
chmod +x empty_text
```
