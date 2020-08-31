import tensorflow as tf


class ConvClassifier(tf.keras.Model):

    def __init__(self):
        super(ConvClassifier, self).__init__()
        filter_base = 128
        filter_multiplicator = 1
        internal_dense_size = 100

        self.predictor = tf.keras.Sequential(
            [
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', strides=2),
                tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same', strides=2),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(internal_dense_size, activation='relu'),
                tf.keras.layers.Dense(1, use_bias=True, activation='sigmoid')
            ]
        )

        self.predictor = tf.keras.Sequential(
            [
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(internal_dense_size, activation='relu'),
                tf.keras.layers.Dense(1, use_bias=True, activation='sigmoid')
            ]
        )

    def call(self, x, training=False):
        x = self.predictor(x)
        return x

    @tf.function
    def train_step(self, data):
        x, y = data

        with tf.GradientTape() as tape:
            y_pred = self(x, training=True)
            loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)

        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        self.compiled_metrics.update_state(y, y_pred)

        return {m.name: m.result() for m in self.metrics}

    @tf.function
    def test_step(self, data):
        x, y = data
        y_pred = self(x, training=False)
        self.compiled_loss(y, y_pred, regularization_losses=self.losses)
        self.compiled_metrics.update_state(y, y_pred)

        return {m.name: m.result() for m in self.metrics}


def TrainConvClassifierModel(train_ds, test_ds, internal_model = None, num_epochs = 10, steps_per_epoch=100000, complete_model = None):

    if complete_model is not None:
        model = complete_model
    else:
        model = ConvClassifier()
        if internal_model is not None:
            model.predictor = internal_model
        model.compile(
            optimizer=tf.optimizers.Adam(learning_rate=0.001),  # 0.001, tf.keras.optimizers.RMSprop(0.001)
            loss=tf.keras.losses.BinaryCrossentropy(from_logits=False),
            metrics=['mae', 'accuracy']
        )

    history = model.fit(
        train_ds,
        validation_data=test_ds,
        epochs=num_epochs,
        steps_per_epoch=steps_per_epoch,
        validation_steps=100,
        verbose=1
    )

    return model, history
