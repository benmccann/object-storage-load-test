package com.benmccann;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.UUID;

import org.apache.commons.io.IOUtils;
import org.jclouds.ContextBuilder;
import org.jclouds.blobstore.AsyncBlobStore;
import org.jclouds.blobstore.BlobStoreContext;
import org.jclouds.blobstore.domain.Blob;
import org.jclouds.logging.slf4j.config.SLF4JLoggingModule;
import org.jclouds.openstack.swift.SwiftApiMetadata;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import com.google.common.collect.ImmutableSet;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.inject.Module;

public class ObjectStorageLoadTest {

  private final BlobStoreContext context;

  public ObjectStorageLoadTest(String user, String password) {
    Iterable<Module> modules = ImmutableSet.<Module>of(new SLF4JLoggingModule());
    this.context = ContextBuilder.newBuilder(new SwiftApiMetadata().toBuilder()
        .defaultEndpoint("https://dal05.objectstorage.softlayer.net/auth/v1.0/").build())
        .credentials(user, password)
        .modules(modules)
        .buildView(BlobStoreContext.class);
  }

  public ListenableFuture<String> putAsync(String fileName, String data) {
    System.out.println("Uploading " + fileName);
    AsyncBlobStore asyncBlobStore = context.getAsyncBlobStore();
    Blob blob = asyncBlobStore.blobBuilder(fileName).payload(data).build();
    return asyncBlobStore.putBlob("loadtest", blob);
  }

  private static class Credentials {
    @Parameter(names = "--username", description = "username")
    public String username;
    
    @Parameter(names = "--password", description = "password")
    public String password;
  }

  public static void main(String[] args) throws IOException {
    final Credentials credentials = new Credentials();
    new JCommander(credentials, args);

    final String data = IOUtils.toString(new FileReader(new File("resources/test.html")));

    for (int i = 0; i < 100; i++) {
      new Thread() {
        @Override
        public void run() {
          ObjectStorageLoadTest loadtest = new ObjectStorageLoadTest(credentials.username, credentials.password);
          while (true) {
            loadtest.putAsync(UUID.randomUUID().toString() + ".html", data);
            try {
              Thread.sleep(1000);
            } catch (InterruptedException e) {
              throw new RuntimeException("Unexpected exception", e);
            }
          }
        }
        
      }.start();
    }
  }

}
