---
source: detectify
source_url: https://labs.detectify.com/security-guidance/leveraging-aws-quicksight-dashboards-to-visualize-recon-data/
title: "Leveraging AWS QuickSight dashboards to visualize recon data - Labs Detectify"
author: "Detectify"
published: 2022-05-30T13:21:08+00:00
description: "Improve data quality from your bug bounty hunts by using AWS QuickSight to develop dashboards to visualize and navigate the data outputs."
---

[Home](https://labs.detectify.com/)/ [Security guidance](https://labs.detectify.com/category/security-guidance/)/ [Leveraging AWS QuickSight dashboards to visualize recon data](https://labs.detectify.com/security-guidance/leveraging-aws-quicksight-dashboards-to-visualize-recon-data/)

[Security guidance](https://labs.detectify.com/category/security-guidance/ "Security guidance")

# Leveraging AWS QuickSight dashboards to visualize recon data

**Ryan Elkins** May 30, 2022

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/leveraging-aws-quicksight-dashboards-to-visualize-recon-data/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/leveraging-aws-quicksight-dashboards-to-visualize-recon-data/ "Share on LinkedIn")

**TL/DR: AWS QuickSight makes it easy to build visualizations, perform ad-hoc analysis, and quickly get business insights from their data, anytime, on any device. Hacker and security researcher Ryan Elkins [(@ryanelkins](https://twitter.com/ryanelkins)) breaks down how you can use it.**

Are you drowning in output files from your bash one-liners? Do you spend hours sifting through the data?

An underutilized opportunity for optimization and analysis is to develop dashboards to visualize and navigate the data outputs from a collection of bug bounty tools. After an initial time investment to configure, these dashboards can provide ongoing filtering to quickly present relevant data.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image6-1.png)

The base setup requires configuration of the services, access, and authorization. Once the dependencies are established, the dashboard will remain up-to-date with the most recent output data from our bug bounty hunts.

There are numerous visualization tools to select from with varying degrees of configuration and tuning required. Some examples include [Microsoft PowerBi](https://powerbi.microsoft.com/), [Tableau](https://www.tableau.com/), [Bokeh](https://bokeh.org/), [Matplotlib](https://matplotlib.org/), [Plotly](https://plotly.com/), [D3.js](https://d3js.org/), and [Seaborn](https://seaborn.pydata.org/). For this walkthrough, we are going to leverage [Amazon QuickSight](https://aws.amazon.com/quicksight/) which is a cloud-native service offering by Amazon Web Services (AWS).

The QuickSight service can ingest and display data from many services although, for this use case, we will utilize [Amazon Simple Storage Service (S3)](https://aws.amazon.com/s3/) as our raw data source. The cloud-based SaaS options eliminate the need for infrastructure support and can scale based on a balance of demand, speed, and cost. The dashboard performance and responsiveness is delivered using a super-fast, parallel, in-memory calculation engine (SPICE).

The dashboards will continually refresh data from an integrated source and newly added data will have immediate visibility and reporting benefits.

In order to maintain consistency and reduce errors, new data is processed through an ETL (extract, transform, and load) process. If you have ever performed engineering to normalize data into a Security Information and Event Management (SIEM) platform for monitoring by a Security Operations Center (SOC), you would have established ETL capabilities.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image32.png)

This walkthrough will comprise of 3 components:

1. Infrastructure/Service Configuration
2. Data Extract, Transform, Load (ETL)
3. Dashboard Generation

The final product will be a sample dashboard with seven key measures. Some of the services do have a minimal cost associated, but if you generate a new AWS account for this tutorial, everything configured is included within the [AWS free tier](https://aws.amazon.com/free/).

## **Infrastructure/Service Configuration**

![](https://labsadmin.detectify.com/app/uploads/2022/05/image29.png)

The configuration section will build the cloud infrastructure depicted above. This tutorial will demonstrate console-based creation although there is tremendous value in building cloud environments using infrastructure as code because it provides change management when tracked in a source code management system such as GitHub, repeatability, consistent deployment, and recovery options.

### **S3 Bucket Creation**

To begin, you will need an AWS S3 bucket to store the data.

- [Login](https://console.aws.amazon.com/) to your AWS account and navigate to the S3 service.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image12-1.png)

- Once you access the service, click “Create bucket”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image13-1.png)

- Provide the bucket with a globally unique name.
- Select a region. Ideally, the region would be near your geographic location although just be sure to create all of the resources within the same region to avoid data transfer costs.
- Object Ownership can remain the default – “ACLs disabled (Recommended)”
- Leave the default “Block all public access” checked.
- Bucket Versioning: disabled.
- Default encryption – Select Enable and then select Amazon S3-managed keys (SSE-S3).

![](https://labsadmin.detectify.com/app/uploads/2022/05/image47.png)

- Select “Create bucket”

Since many of us will be working from a non-GUI virtual private server (VPS) or Linux server, we will want to transfer the files directly to the newly created S3 bucket. In order to do that, we need to establish authentication and authorization.

### **Create an IAM policy**

- Search for and select the IAM service.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image48.png)

- Then select policies.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image43.png)

- Within the Create policy Visual editor, search and select the S3 service.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image41.png)

- Expand the “Actions” section, expand “Write”, and select the “PutObject” permission.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image7-1.png)

- Enter the Bucket name \[the bucket that was previously created\].
- Add an asterisk to permit PUT Object actions for any file in the bucket.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image54.png)

- Click “Add”
- Click “Next: Tags”
- No tags are needed. Click “Next: Review”
- Provide a Name and Description for the policy. The completed policy should look like the following:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image4-1-1.png)

- Click “Create policy”

### **Create an IAM programmatic user**

- Open the IAM service and select Users.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image17-1.png)

- Click “Add users”
- Provide a User name value.
- Select the box for “Access key – Programmatic access” and leave the “Password – AWS Management Console access” box unchecked. Leaving the box unchecked provides additional security value by not introducing a password to the user which would be in addition to the programmatic access secret key.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image8-1-1.png)

- Click “Next: Permissions”
- Select “Attach existing policies directly”. It is best practice to assign policies to groups and then add users into the group but for limiting steps within this demo, the policy can be attached directly to the user.
- Within the “Filter policies” section, type the name of the previously created policy and check the box to assign it to the user.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image3-1.png)

- There is no need to configure a boundary policy.
- Click “Next: Tags”
- No tags are needed. Click “Next: Review”
- The review summary should look similar to the following:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image55.png)

- Click “Create user”
- This screen is the only opportunity that will be provided to retrieve the secret key for the user. The best option is to likely click “Download .csv” or if you have a password manager readily available, you can copy the Access key ID and the Secret access key directly to the vault. This will be utilized within the command line on our hacking server.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image49.png)

### **Completion of the AWS dependency configurations**

At this point, the AWS environment should have:

- S3 bucket for data storage.
- IAM policy granting least privilege access to the S3 bucket.
- Programmatic user account with the IAM policy attached for uploading the target data to the S3 bucket.

## **Data Extract, Transform, and Load (ETL)**

The next step is to actually collect the data and normalize it to be published within the QuickSight dashboard. This use case will build the dashboards based on the raw JSON output files from a tool developed by [Projectdiscovery](https://projectdiscovery.io/#/) called [httpx](https://github.com/projectdiscovery/httpx). It has a rich dataset within the output and gives us extensive options to visualize.

If you already have [httpx](https://github.com/projectdiscovery/httpx) data output, you can skip this step or modify the schema and dashboard steps to match the specific data that you plan to utilize. For simplicity, we will not need to modify the httpx output for this tutorial. Some of the power in AWS QuickSight is that it can auto-detect the schema. If we were trying to analyze files from different sources, we would need to normalize the keys, data types, and format into a consistent JSON schema.

### **Install the dependent tools**

To generate the data for the dashboard, your environment will need both Go and Python 3 installed.

- Ensure that go is installed. The OS specific steps to install it are at [https://go.dev/doc/install](https://go.dev/doc/install).
- Install Python 3 if it is not already installed. The OS specific steps are at [https://www.python.org/downloads/](https://www.python.org/downloads/).
- Install httpx:

`````` go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest```

- Install [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html):

`````` curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"```

`````` unzip awscliv2.zip```

`````` sudo ./aws/install```

If you do not already have an existing URL list, you can install the following tools to generate a scoped URL list:

- Install [hakrawler](https://github.com/hakluke/hakrawler) for web crawling:

`````` go install github.com/hakluke/hakrawler@latest```

### **Generate a URL list**

If you do not have an existing URL list, you can select one of the following three options to generate the httpx output for this walkthrough:

1. Use your own URL list and name it urls.txt to conform with the commands within the walkthrough.

`````` cat urls.txt | httpx --json -o demo-httpx.json -sc -cl -ct -rt -lc -wc -title -server -td -method -ip -cname -asn -cdn```

1. Download a list of sample URLs.

`````` curl https://raw.githubusercontent.com/brevityinmotion/goodfaith/main/samples/brevityinmotion-urls-max.txt --output urls.txt```

Once the urls.txt file is downloaded, run the following to generate the dashboard data file:

`````` cat urls.txt | httpx --json -o demo-httpx.json -sc -cl -ct -rt -lc -wc -title -server -td -method -ip -cname -asn -cdn```

1. Generate a list of URLs from a bug bounty target. Example command (you can customize the URL in the echo statement):

````
``` echo https://www.brevityinmotion.com | hakrawler | httpx --json -o demo-httpx.json -sc -cl -ct -rt -lc -wc -title -server -td -method -ip -cname -asn -cdn
````

This command will pass a URL to be crawled by [hakrawler](https://github.com/hakluke/hakrawler) and then the discovered URLs will be piped to httpx to initiate requests and collect the URL information.

### **Update the configuration file**

All three options will create a JSON based output file called demo-httpx.json and will be the data file for the dashboard.

In order to ingest the data into AWS QuickSight, we will need to upload a manifest file to the S3 bucket. An example manifest template can be downloaded using the following command:

`````` curl https://raw.githubusercontent.com/brevityinmotion/goodfaith/main/samples/manifest-s3-httpx.json --output manifest-s3-httpx.json```

Using your favorite text editor (i.e. nano manifest-s3-httpx.json), make sure to modify the URIPrefixes to reflect the bucket specific to your environment.

- The URIPrefixes will be the bucket name and path to the data to be visualized.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image23-1.png)

### **Load the data**

Once the data is ready, the AWS credentials need to be configured for the IAM user previously configured. There are [multiple methods](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) for establishing AWS cli credentials. The AWS region is in the format of us-east-1 and the following commands can be utilized:

`````` export AWS_ACCESS_KEY_ID={PASTE ACCESS KEY FROM AWS USER}```

`````` export AWS_SECRET_ACCESS_KEY={PASTE SECRET KEY FROM AWS USER}```

`````` export AWS_DEFAULT_REGION={aws-region}```

Once the environmental variables are set, run the following:

`````` aws s3 cp manifest-s3-httpx.json s3://brevity-dashboard/config/manifest-s3-httpx.json```

`````` aws s3 cp demo-httpx.json s3://brevity-dashboard/data/demo-httpx.json```

Once these steps are completed, they will be visible when browsing the objects in the S3 bucket from the AWS console.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image33.png)

## **Dashboard Generation**

The final section of the tutorial is to create, customize, and publish the dashboard for consumption.

### **Configuring AWS QuickSight**

To configure AWS QuickSight, begin by searching for QuickSight within the AWS console search pane and then open QuickSight.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image26.png)

The next step is to create a QuickSight account which will require you to submit your email address.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image45.png)

- Click Continue

Note: as mentioned earlier, AWS QuickSight has a 30 day free trial period which is sufficient to cover this walkthrough although it will cost [$12/user/monthly](https://aws.amazon.com/quicksight/pricing/) ongoing. Make sure to delete the created user within the “Manage QuickSight” profile section before the end of the trial to avoid the ongoing costs.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image37.png)

Prior to connecting to the Dataset, we will need to grant the QuickSight service access to the S3 data.

- In the top right corner, click on your user id and select “Manage QuickSight”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image30.png)

- In the left-column, select “Security & permissions”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image11-1.png)

- Once the QuickSight service is loaded, click on “Datasets”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image5-1-1.png)

- Within the “QuickSight access to AWS services” section, click “Manage”.
- Check the box for “Amazon S3” and then click “Select S3 buckets”.
- In the next window, make sure to check the box for the S3 bucket containing the data and then click “Save”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image46.png)

### **QuickSight data source connection**

At this point, we are ready to create the data source connection.

- Return to the main QuickSight page by clicking the logo in the top left corner.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image24.png)

- Click on “Datasets” from the left-pane menu.
- Select “New dataset” from the top right-corner.
- Select the “S3” data source.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image35.png)

- Upon clicking S3, it will introduce a window to configure the New S3 data source.
- To retrieve the manifest file URL from the bucket, using a new tab or window, you can navigate to the file within the S3 service, select the object, and click “Copy URL”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image52.png)

- Provide a name for the data source.
- Select URL has the radio button option.
- Paste the copied URL from S3 to point to the manifest file.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image34.png)

- Click “Connect”.
- If the connection is successful and discovers the manifest file, the return result will provide a set of options.
- Click on “Edit/Preview data”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image18-1.png)

Initially, there will be no data shown because the data import fails due to the format of the timestamp field. Although there is an error in the initial process, it still saves time because it auto-detects and applies the column types. When there are data processing issues, it is typically a type formatting error or mismatch that can be quickly resolved.

- To resolve the issue, click on “timestamp” and change the “Date” format to “String” by clicking on the “Date” and selecting “String”. Completion of this step will resolve the data import issue.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image16-1.png)

Upon completion, the data load will refresh and the table will be populated with data from the httpx json file.

- To save the data connector, click “Save & publish” in the top right corner.
- Next, click the “Publish & visualize” button to move to the next step.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image1-1.png)

Often, the top right corner will have a status box of the data ingestion. It is important to monitor it to ensure 100% ingestion of data and then resolve any issues if they arise.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image19-1.png)

### **Develop the dashboard**

For this tutorial, we will create seven valuable measurements to publish into the dashboard. This is where you can tweak and customize to either copy these directly, adjust them to your objective outcomes, or creatively develop brand new insights.

In the prior step, if you clicked “Publish & visualize” you will already have Analysis to develop. Otherwise, you can select the newly created Dataset and click “Create analysis”.

To access the Analysis object, click “Analyses” on the left pane of the main QuickSight page. This will display all of the objects.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image2-1.png)

Select the intended Analysis to modify.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image51.png)

#### **Measurement \#1 – Count of URLs by status code**

Status codes are useful and may indicate the type of attack necessary such as authentication bypass if a lot of 403 status codes are returned. It may also highlight unique status codes which may indicate further investigation.

- With the Visualize tab selected on the left panel, click on the “status-code” field.
- Select the “Donut chart” visual type.
- At the top, there is a “Field wells” section and the “Value” column will be blank. Click on “Value” to expand the section.
- Drag and drop the “url” field into the value box and ensure that the calculation is “Count”. The Field wells should look like the below image.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image25.png)

- The title can be updated by double-clicking on the default text.
- The box size can be adjusted and dragged to a desirable location on the dashboard.

#### **Measurement \#2 – Count of Unique URLs**

- Click on URL field.
- Select the “Insight” (lightbulb) visual type.
- To modify the Insight text, click the ellipsis (…) on the right side of the box and then click “Customize narrative”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image53.png)

- In the Computations box, the categoryField should have uniqueGroupValuesCount.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image38.png)

- The narrative text can be modified to:

“There were UniqueGroupValues.uniqueGroupValuesCount unique URLs across the dataset.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image15-1.png)

- The completed visual will be:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image40.png)

#### **Measurement \#3 – Count of URLs by IP Address**

The value of this metric highlights the size of a website running on a single or set of IP addresses. Large numbers of URLs on an IP address may indicate more attack surface.

- Click on the “host” field.
- Select “Vertical bar chart” as the visual type.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image22-1.png)

#### **Measurement \#4 – Count of URLs by Web Server**

A review of the composition and specific hosting web servers may indicate vulnerable platforms.

- Click on the “webserver” field.
- Select “Pie Chart” as the visual type.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image27.png)

#### **Measurement \#5 – Count of URLs by ASN**

An autonomous system number (ASN) is assigned to a corporation or entity and includes a block of IP addresses assigned. This information can provide insight into the various hosting services for a target.

- Click on the “asn.as-name” field.
- Select “Funnel chart” as the visual type.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image14-1.png)

#### **Measurement \#6 – Geographic visual of ASN country origins**

- Select the “asn.as-country” field.
- Select the “Points on map” visual type.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image10-1.png)

#### **Measurement \#7: Filter table based on URL title**

With a small sample set, this is not as effective, but when this analysis scales across millions of URLs, you can add a listing of OR filter conditions such as “admin”, “dashboard”, “error”, “tomcat”, etc. to quickly identify URLs of interest.

- Select the “title” field.
- Select the “Table” visual type.

In order to maximize the value of this table, a filter can be added.

- With the Table selected, click the “Filter” tab on the left-side.
- Click “Create one…”

![](https://labsadmin.detectify.com/app/uploads/2022/05/image31.png)

- Select the “Title” field as the filter.
- Click on “Include all” to expand the options.
- For filter type, select “Custom filter” and select “Contains”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image39.png)

- Once the selections are added, click “Apply”.
- If prompted on whether to change the scope of the filter, select “No”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image20-1.png)

- The filtered table will look like:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image50.png)

#### **Quick Insights**

In order to add additional visuals, the “Insights” tab can be selected and it will provide a listing of pre-made options to add.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image44.png)

#### **Publishing the Dashboard**

Once all of the visuals are organized across the Analysis window, the analysis is ready to be published as a Dashboard.

- In the top right corner, select “Share” and click “Publish dashboard”.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image9-1-1.png)

- Add the additional checkbox to “Enable ad hoc filtering” as this is convenient as a single user of the dashboard.
- If collaborating with others, sometimes the details behind the visuals may need to remain protected. This is where the download options can be disabled.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image21-1.png)

- Click “Publish dashboard”.
- The final dashboard will be available for ongoing analysis as data is added to the S3 bucket.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image6-1-1.png)

## **Expanding the usage**

This is only a small use case for beginning the journey into data dashboards and visualizations. The capabilities that can integrate with object-based storage in AWS S3 are very powerful and often underutilized in the hacker community. All future output files added to the bucket will be ingested and displayed when the dataset is refreshed and the solution can scale as the dataset grows. Ad-hoc filtering will result in subsets of data that can be downloaded and further leveraged in bug bounty workflows. As we search for anomalies and outliers, visual images and insights make it much more efficient for the human brain to identify records of interest to further triage and investigate. Happy hunting!

## **Written by:**

Ryan Elkins [(@ryanelkins](https://twitter.com/ryanelkins)) who has over 15 years of experience leading security architecture and application security programs across multiple industries. Ryan is passionate about software security, cloud automation, sharing knowledge, and supporting other creators. You can learn more at his [blog](https://www.brevityinmotion.com/) or on [GitHub](https://github.com/brevityinmotion).

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/leveraging-aws-quicksight-dashboards-to-visualize-recon-data/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/leveraging-aws-quicksight-dashboards-to-visualize-recon-data/ "Share on LinkedIn")

**Ryan Elkins**

Security Architecture and Application Security Leader

## Check out more content

The smaller our attack surface, the fewer things we need to worry about. An excellent way of reducing the attack surface (and our cognitive load) is using AWS Service Control Policies (SCPs.) In this post, I’ll describe how we approached it.

March 26, 2024

It’s no secret that cloud architectures have several characteristics that make SSRF attacks challenging to defend against. While SSRFs are not a new threat vector, …

September 23, 2022

TL/DR: On December 2, open-source analytics solution Grafana released an emergency security patch for critical zero-day Path Traversal vulnerability CVE-2021-43798, after proof-of-concept code to exploit …

December 15, 2021

Crowdsource hackers Hakluke and Farah Hawa share the top web vulnerabilities that are often missed during security testing. When hunting for bugs, especially on competitive bug bounty …

September 30, 2021