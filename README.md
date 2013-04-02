This writes to a container named 'loadtest' in the SoftLayer dal05 data center.

The Java version should be preferred because the Python stuff here reacts poorly to [SoftLayer's seemingly broken servers](https://github.com/softlayer/softlayer-object-storage-python/issues/17).

Install [Gradle](http://www.gradle.org/) and then run:

    gradle run -Pargs="--username xxx --password xxx"
