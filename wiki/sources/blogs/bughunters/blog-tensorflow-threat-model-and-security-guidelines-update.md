---
source: bughunters
source_url: https://bughunters.google.com/blog/tensorflow-threat-model-and-security-guidelines-update
title: "TensorFlow Threat Model and Security Guidelines Update - Google Bug Hunters"
description: "We are excited to announce an update to the TensorFlow threat model, providing updates to security recommendations, clear examples, and a baseline for defining scope in the Google Vulnerability Reward Program."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/tensorflow-threat-model-and-security-guidelines-update#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# TensorFlow Threat Model and Security Guidelines Update

![](https://storage.googleapis.com/bughunters-article-images/blogs/jduart.jpg)

Jose Duart

Information Security Engineer

Published: Feb 5, 2024

Vulnerability Reward Program  Security Engineering

[RSS Feed](https://bughunters.google.com/feed/en)

# TensorFlow Threat Model and Security Guidelines Update

We are excited to announce an update to the
[TensorFlow threat model](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md).
This new threat model updates the security recommendations, provides clear
examples, and serves as a baseline to define scope in the Google Vulnerability
Reward Program. Read on to see what has changed and the reasons behind the
changes.

## Why were the changes necessary?

Google had internal security guidelines about how to use TensorFlow, developed
by the Google Information Security Engineering (ISE) team. However, these
guidelines were not entirely in line with the previous TensorFlow threat model
published in the official TensorFlow repository. These differences added
complexity to the internal evaluation of bug reports, and made it more difficult
to prioritize fixes according to impact.

A product of a collaboration between ISE, the TensorFlow Security team, and the
Google Vulnerability Reward Program (VRP), the new threat model is more specific
in describing the risks and what issues are in scope for the VRP. This detailed
information and the clear examples of what we consider risky should help users
securely design their projects that depend on TensorFlow. The defined VRP scope
suggests interesting areas of research, where findings will result in more
valuable security reports.

## TensorFlow models are programs

One of the main changes made in the new threat model is that we adjusted the
impact of memory corruption issues triggered when running user-provided
TensorFlow models. Since running untrusted programs is equivalent to giving code
execution, triggering memory corruption issues in that context does not give any
extra access or capabilities. An attacker could just
[embed a reverse shell in the model](https://splint.gitbook.io/cyberblog/security-research/tensorflow-remote-code-execution-with-malicious-model)
and execute commands as the user running the TensorFlow service. For that
reason, crashes that are triggered from user-provided models are not considered
a priority as they don’t break a security boundary and therefore are left out of
scope for the VRP. This also applies to saved models because they are serialized
representations of the model/program.

Does this mean that no memory issues or crashes are in scope for the VRP? Not
exactly, it might still be possible to trigger some of these issues in existing
production models through special inputs or actions during training or serving.
To cover these scenarios, if you can reproduce the issue using an
Alphabet-authored model from tfhub.dev (without custom modifications), that will
be considered in scope.

For example, in Google’s
[mobilebert implementation](https://github.com/google-research/google-research/blob/master/mobilebert/run_squad.py),
if you control the contents of the `data_dir` directory, would you be able to
trigger issues in the model calls to `train()` or `predict()`?

### A more detailed example

Let’s take a look at an example that showcases a potential TensorFlow operation
vulnerability and reachability from the prediction interface of the model.
Imagine that one of the Alphabet-published models is processing text and
implementing a bag of words model, with the particularity that it decided to use
a `SparseTensor` to store the one-hot encoding of the words present in a
document. That could look something like:

```
vocab_terms = tf.constant(vocab.split())
vocab_indexes = tf.constant(list(range(len(vocab.split()))))
# This creates a lookup table that returns ids for the words of
# our vocabulary.
table = tf.lookup.StaticHashTable(
   tf.lookup.KeyValueTensorInitializer(vocab_terms, vocab_indexes),
   default_value=-1)

def encode_one_hot (input_tensor, table):
   '''Convert input_tensor into a sparse tensor.'''
   encoded = table[input_tensor]
   # encoded has values as [1, 2, 3, 4] but SparseTensor
   # indices should be in the form [[1], [2], [3], [4]]
   reshaped = tf.reshape(encoded, [tf.shape(input_tensor)[0], 1])
   # 1-dimensional tensor with [1]'s for the one-hot encoding.
   sparse_values = tf.constant([1] * len(encoded))

   return tf.sparse.SparseTensor(indices=reshaped.numpy(), values=sparse_values, dense_shape=[VOCAB_SIZE])
```

This code has a small issue. If `input_tensor` contains a term that is not
present in the predefined vocabulary, then `StaticHashTable` will return a -1
(because it is defined as the `default_value`) and the code will use that as an
index for the sparse tensor. Sparse tensors don’t mind working with negative
indexes, but will run into trouble when trying to convert these indexes it into
a dense tensor:

```
>>> print(sparse)
SparseTensor(indices=tf.Tensor(
[[ 5]\
 [ 1]\
 [-1]], shape=(3, 1), dtype=int64), values=tf.Tensor([1 1 1], shape=(3,), dtype=int32), dense_shape=tf.Tensor([6], shape=(1,), dtype=int64))

>>> print(tf.sparse.to_dense(tf.sparse.reorder(sparse)))
InvalidArgumentError: {{function_node __wrapped__SparseToDense_device_/job:localhost/replica:0/task:0/device:CPU:0}} indices[0] = [-1] is out of bounds: need 0 <= index < [5000] [Op:SparseToDense]
```

That means that our example model can easily be crashed by simply providing
inputs that get encoded by the prediction API. A DoS is not bad, but can we do
better than that? Interestingly, if we trace the error we can find
[the code implementing the checks](https://github.com/tensorflow/tensorflow/blob/cd3c543b403a06a4d7d58008756a813139ffa754/tensorflow/core/util/sparse/sparse_tensor.cc#L121)
on the indexes:

```
bool SparseTensor::IndicesValidVectorFastPath() const {
  DCHECK_EQ(shape_.size(), 1);
  DCHECK_EQ(order_[0], 0);

  const int64_t max_index = shape_[0];

  // We maintain separate bools for each validation predicate to enable
  // vectorization across loop iterations.
  bool index_in_range_valid = true;
  bool order_valid = true;

  int64_t prev_index = -1;
  const auto ix_t = ix_.matrix<int64_t>();
  const int64_t* const index_base_ptr = ix_t.data();

  for (std::size_t n = 0; n < ix_t.dimension(0); ++n) {
    const int64_t index = index_base_ptr[n];
    index_in_range_valid = index_in_range_valid & (index < max_index);
    order_valid = order_valid & (index > prev_index);
    prev_index = index;
  }

  return index_in_range_valid & order_valid;
}
```

The indices of our sparse tensor are stored in `index_base_ptr`. These are then
checked to ensure they are smaller than the maximum and are stored in order
(smallest to largest). Do you notice something missing? Exactly, the index is
not directly checked to be negative, only indirectly via the order check.
Without that lucky check, the sparse tensor would be considered valid and could
end up causing a memory out-of-bounds access when used by other operations.

Although this example used a non-exploitable issue, we hope that it illustrates
how a memory corruption issue in a TensorFlow operation could still be in scope
for the VRP if it can be triggered via a real model.

## Compiling untrusted models

As pointed out in the threat model, compiling models via the documented and
recommended entry points described in the [XLA](https://www.tensorflow.org/xla)
and [JAX](https://jax.readthedocs.io/en/latest/jax-101/02-jitting.html)
documentation is considered safe even when compiling untrusted models, because
the models are not executed during the compilation process (note that the
compiled form of an untrusted model should still be considered untrusted when
executed).

The compiler also includes a set of tools designed for internal use. The purpose
of these tools is testing and debugging. They are not intended to be used in
production and they're not safe to use with untrusted data or models. Most of
these tools live under the
[compiler source tree](https://github.com/tensorflow/tensorflow/tree/master/tensorflow/compiler)
in various sub-directories named `tests/`, `utils/`,`tools/`, etc. While they
might be interesting to use during research and as fuzzing targets, they’re not
the recommended compiler APIs and therefore issues discovered through those
tools would only be in scope for the VRP if they are reachable from the
documented compiler APIs linked above (for example, compiler issues that can be
triggered in a model using `jit_compile=True`).

## Working with untrusted checkpoints

Although it is not a common design pattern to let users provide
[checkpoints](https://www.tensorflow.org/guide/checkpoint) to be loaded into the
model, it’s still possible to design a ML application in that way so we wanted
to briefly cover the security implications here.

The risk of loading untrusted checkpoints is not as obvious as with models. If
TensorFlow models are programs, then loading attacker-controlled checkpoints
would be similar to letting the attacker control the values of variables inside
a program. The risk of this scenario depends on what the program (or the model
in the TensorFlow context) does with these variables. If the variables are only
used to generate predictions, they can obviously have a strong influence or
directly control the prediction output, but other than that they’re not that
interesting from an attacker’s perspective.

However, if these variables are used to configure how the model interacts with
the system that is running it (for example defining filesystem paths or network
endpoints that the model uses), then that would allow an attacker who is able to
control the checkpoints to modify these interactions and make the model do
things that it was not expected to do.

The general guideline here is to avoid loading untrusted checkpoints and, in
cases where it is necessary, add some sort of validation to the values that
limits how an attacker could influence the model’s behavior.

## Training and prediction

Another important change that the new threat model includes is more detail on
the risks around training and prediction/serving.

Both steps are commonly exposed to untrusted data, and given that sandboxing
these processes consumes (a potentially large amount of) extra resources, we
wanted to clearly define which processes should be safe to use without a sandbox
and where we recommend using a sandbox when processing untrusted data. An
alternative to sandboxing would be to design the system in a way that the
conversion from the input format into tensors happens in an external
environment/process.

The risk decision regarding these format parsing libraries was based on a number
of factors, including vulnerability history, complexity of the code parsing the
input format, whether these libraries have working fuzz tests, what their
fuzzing coverage is, and several more. While that doesn’t guarantee that these
libraries are going to be free of bugs, we expect that issues with a security
impact will be rare and that’s why these kinds of issues are in scope
for the VRP.

For the libraries where we don't have that confidence and that are considered
out of scope for the VRP, we recommend reporting any issues directly to the
maintainers. As a long-term mitigation, TensorFlow has plans to work on features
that would easily enable sandboxing on their input parsing where necessary. In
the meantime, our recommendation is to sandbox the preprocessing of the data, or
the whole model execution if preprocessing and model execution cannot be split
easily.

## Eager mode considerations

One last thing that we would like to cover before wrapping up this post is the
difference between _Eager_ mode and other execution modes. _Eager_ mode, which
is the default mode in TensorFlow v2, lets users write statements that are
processed sequentially, and where each operation has its inputs and outputs with
specific values.

This contrasts with other execution modes, where the model declares operations
that build an
[execution graph](https://www.tensorflow.org/guide/intro_to_graphs#what_are_graphs).
Here, the shapes or types of parameters are not known, so when the graph is
created, there’s a process called tracing that tries to infer properties of the
parameters and optimize accordingly. That tracing step is also in charge of
detecting errors, even before having to execute any of the operations with real
data. The errors are detected via checks implemented in
“ [shape inference](https://www.tensorflow.org/guide/create_op#define_the_op_interface)”
functions. For example, in the `ParallelConcat` [operation](https://github.com/tensorflow/tensorflow/blob/cd8ec9b28db7deef0becb603de9b4f5a28edb855/tensorflow/core/ops/array_ops.cc#L288C1-L294C42),
the shape inference function (defined via `SetShapeFn`) checks that all input
shapes are defined, that ranks for all the inputs are greater than 0, and that
the size of the first dimension is 1 (you can find these checks by looking for
all code paths that end returning an `InvalidArgument`).

How is all of this related to the security properties of TensorFlow? In _Eager_
mode, shape inference functions are not executed. Therefore, some security
checks are not performed, like for example preventing passing a 0-ranked input
to `ParallelConcat` following the example above. Without these checks, there’s a
higher chance for inputs to be able to cause crashes and potentially some
security issues.

Based on that increased risk, the recommendation is to avoid using _Eager_ mode
for production if the model is going to be exposed to untrusted inputs. As a
consequence, crashes or issues that can only be triggered in _Eager_ mode are
considered out of scope for the VRP.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab