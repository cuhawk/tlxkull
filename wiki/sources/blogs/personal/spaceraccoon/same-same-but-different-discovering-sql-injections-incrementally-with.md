---
source: spaceraccoon
source_url: https://spaceraccoon.dev/same-same-but-different-discovering-sql-injections-incrementally-with/
title: "Same Same But Different: Discovering SQL Injections Incrementally with Isomorphic SQL Statements | Spaceraccoon's Blog"
published: 2020-04-05T09:04:58+00:00
description: "Despite the increased adoption of Object-Relational Mapping (ORM) libraries and prepared SQL statements, SQL injections continue to turn up in modern applications. In real-world scenarios, researchers need to balance two concerns when searching for SQL injections - 1. Ability to execute injections in multiple contexts; and 2. Ability to bypass WAFs and sanitization steps. A researcher can resolve "
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Same Same But Different: Discovering SQL Injections Incrementally with Isomorphic SQL Statements

Apr 5, 2020
·

1219 words

·

6 minute read


# Motivation [🔗](https://spaceraccoon.dev/same-same-but-different-discovering-sql-injections-incrementally-with/\#motivation)

Despite the increased adoption of Object-Relational Mapping (ORM) libraries and prepared SQL statements, SQL injections continue to turn up in modern applications. Even ORM libraries have [introduced SQL injections](https://snyk.io/vuln/npm:sequelize:20160106) due to mistakes in translating object mappings to raw SQL statements. Of course, legacy applications and dangerous development practices also contribute to SQL injection vulnerabilities.

Initially, I faced difficulties identifying SQL injections. Unlike another common vulnerability class, Cross-Site Scripting (XSS), endpoints vulnerable to SQL injections usually don’t provide feedback on where and how you’re injecting into the SQL statement. For XSS, it’s simple: with the exception of Blind XSS (where the XSS ends up in an admin panel or somewhere you don’t have access to), you always see where your payload ends up in the HTML response.

For SQL injections, the best case scenario is that you get a verbose stack trace that tells you exactly what you need:

```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/html; charset=utf-8

<div id="error">
    <h1>Database Error</h1>
    <div class='message'>
        SQL syntax error near '''' where id=123' at line 1: update common_member SET name=''' where id=123
    </div>
</div>
```

If you see this, it’s your lucky day. More often, however, you will either get a generic error message, or worse, no error at all - only an empty response.

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "users": []
}
```

As such, hunting SQL injections can be arduous and time-consuming. Many researchers prefer to do a single pass with automated tools like [sqlmap](https://github.com/sqlmapproject/sqlmap) and call it a day. However, running these tools without specific configurations is a blunt instrument that is easily detected and blocked by Web Application Firewalls (WAF). Furthermore, SQL injections occur in unique contexts; you might be injecting after a `WHERE` or `LIKE` or `ORDER BY` and each context requires a different kind of injection. This is even before various sanitization steps are applied.

Polyglots help researchers use a more targeted approach. However, polyglots, by their very definition, try to execute in multiple contexts at once, often sacrificing stealth and succinctness. Take for example the [SQLi Polyglots](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/Polyglots/SQLi-Polyglots.txt) from Seclists:

```sql
SLEEP(1) /*' or SLEEP(1) or '" or SLEEP(1) or "*/
SLEEP(1) /*' or SLEEP(1) or '" or SLEEP(1) or "*/
IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1))/*'XOR(IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1)))OR'|"XOR(IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),​SLEEP(1)))OR"*/
```

Any half-decent WAF would pick up on these payloads and block them.

In real-world scenarios, researchers need to balance two concerns when searching for SQL injections:

1. Ability to execute and thus identify injections in multiple contexts
2. Ability to bypass WAFs and sanitization steps

A researcher can resolve this efficiently with something I call Isomorphic SQL Statements (although I’m sure other researchers have different names for it).

# Incremental Approaches to Discovering Vulnerabilities [🔗](https://spaceraccoon.dev/same-same-but-different-discovering-sql-injections-incrementally-with/\#incremental-approaches-to-discovering-vulnerabilities)

Going back to the XSS analogy, while XSS scanners and fuzzing lists are a dime a dozen, they usually don’t work too well due to the above mentioned WAF blocking and unique contexts. Recently, more advanced approaches to automated vulnerability discovery have emerged which try to address the downsides of bruteforce scanning, like James Kettle’s [Backslash Powered Scanning](https://portswigger.net/research/backslash-powered-scanning-hunting-unknown-vulnerability-classes). As Kettle writes,

> Rather than scanning for vulnerabilities, we need to scan for interesting behaviour.

In turn, automation pipeline tools like Ameen Mali’s [qsfuzz](https://github.com/ameenmaali/qsfuzz) and Project Discovery’s [nuclei](https://github.com/projectdiscovery/nuclei) test against defined heuristic rules (“interesting behaviour”) rather than blindly bruteforcing payloads. This is the path forward for large-scale vulnerability scanning as more organizations adopt WAFs and better development practices.

For example, when testing for an XSS, instead of asking “does an alert box pop when I put in this payload?”, I prefer to ask “does this application sanitize single quotes? How about angle brackets?” The plus side of this is that you can easily automate this on a large scale without triggering all but the most sensitive WAFs. You can then follow up with manual exploitation for each unique context.

The same goes for SQL injections. But how do you formulate your tests without any feedback mechanisms? Remember that SQL injections differ from XSS in that usually no (positive) response is given. Nevertheless, one thing I’ve learned from researchers like [Ian Bouchard](https://twitter.com/corb3nik) is that even no news is good news.

This is where Isomorphic SQL Statements come into play. Applied here, isomorphic simply means SQL statements that are written differently but theoretically should return the same output. However, the difference is that you will be testing SQL statements which include special characters like `'` or `-`. If the characters are properly escaped, the injected SQL statement will fail to evaluate to the same result as the original. If they aren’t properly escaped, you’ll get the same result, which indicates an SQL injection is possible.

Let’s illustrate this with a simple toy SQL injection:

```sql
CREATE TABLE Users (
    ID int key auto_increment,
    LastName varchar(255),
    FirstName varchar(255),
    Address varchar(255),
    City varchar(255)
);

INSERT INTO Users (LastName, FirstName, Address, City) VALUES ('Bird', 'Big', '123 Sesame Street', 'New York City');

INSERT INTO Users (LastName, FirstName, Address, City) VALUES ('Monster', 'Cookie', '123 Sesame Street', 'New York City');

SELECT FirstName FROM Users WHERE ID = <USER INPUT>;
```

If you are fuzzing with a large list of SQL polyglots, it would be relatively trivial to pick up the injection, but in reality the picture will be complicated by WAFs, sanitization, and more complex statements.

Next, consider the following statements:

```sql
SELECT FirstName FROM Users WHERE ID = 1;
SELECT FirstName FROM Users WHERE ID = 2-1;
SELECT FirstName FROM Users WHERE ID = 1+'';
```

They should all evaluate to the same result if the special characters in the last two statements are injected unsanitized. If they don’t evaluate to the same results, the server is sanitizing them in some way.

![DB Fiddle](https://spaceraccoon.dev/images/5/db_fiddle.png)

Now consider a common version of a search query, `SELECT Address FROM Users WHERE FirstName LIKE '%<USER INPUT>%' ORDER BY Address DESC;`:

```sql
SELECT Address FROM Users WHERE FirstName LIKE '%Big%' ORDER BY Address DESC;
SELECT Address FROM Users WHERE FirstName LIKE '%Big%%%' ORDER BY Address DESC;
SELECT Address FROM Users WHERE FirstName LIKE '%Big%' '' ORDER BY Address DESC;
```

Simply by injecting the same special character `%` twice in the second statement, we are given a clue about the actual SQL statement you are injecting into (it’s after a `LIKE` operator) if you receive the same response back.

Even better, as [Arne Swinnen](https://www.arneswinnen.net/2013/09/automated-sql-injection-detection/) noted way back in 2013 (a pioneer!):

> Strings: split a valid parameter’s string value in two parts, and add an SQL string concat directive in between. An identical response for both requests would again give you reason to believe you have just hit an SQL injection.

We can achieve the same isomorphic effect for strings as numeric IDs simply by adding `' '` to our injection in the third statement. This is interpreted as concatenating the original string with a blank string, which should also return the same response while indicating that `'` isn’t being properly escaped.

From here, it is a simple matter of experimenting incrementally. You thus achieve two objectives:

1. Discover which injectable characters are entered unsanitized into the final SQL statement
2. Discover the original SQL statement you are injecting into

# Mass Automation and Caveats [🔗](https://spaceraccoon.dev/same-same-but-different-discovering-sql-injections-incrementally-with/\#mass-automation-and-caveats)

The goal of this is not only to discover individual SQL injections, but to be able to automate and apply this across large numbers of URLs and inputs. Traditional SQL injection payload lists or scanners make large-scale scanning noisy and resource-intensive. With the incremental isomorphic approach, you apply a heuristic rule like:

```python
if (id_input_response) == (id_input_response + "+''"):
    return true
else:
    return false
```

This is much lighter and faster. Of course, while you gain in terms of fewer false negatives (e.g. polyglots that work but are blocked by WAFs), you lose in terms of more false positives. For example, there are cases where the backend simply trims all non-numeric characters before entering an SQL statement, in which case the above isomorphic statement would still succeed. Thus, rather than relying on a single isomorphic statement (binary signal), you will want to watch for multiple isomorphic statements succeeding (spectrum signal).

Although SQL injections are getting rarer, I’ve still come across them occasionally in manual tests. A mass scanning approach will yield even better results.

[web](https://spaceraccoon.dev/tags/web)