# Kubeflow Pipelines SDK
# https://www.kubeflow.org/docs/pipelines/sdk/sdk-overview/
# installed with `pip install kfp`
import kfp


# What is happening:
# 1. define custom operations based on default operations defined in the Kubeflow Pipelines Domain-specific Language
# 2. use the custom operation to define your pipeline in a function decorated with @kfp.dsl.pipeline
# 3. use kfp.compiler.Compile() to generate a ZIP file containing Argo YAML Manifests that Kubeflow understands
# 4. upload the ZIP file to Kubeflow Pipelines Web UI to define new version of your pipeline
# NB. as the tasks have no relation to each other, the tasks will be executed in unpredictable order
# NB. sometimes containers finish too fast for monitoring so we sleep a bit on each task


def echo_op(text):
    return kfp.dsl.ContainerOp(
        name='echo',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "$0" && sleep 1', text],
    )


@kfp.dsl.pipeline(
    name='Simple Tasks - Echo Chamber',
    description='The simplest example; use shell to echo the three given values as disconnected tasks.'
)
def echo_chamber_pipeline(
        first_text='1st!',
        second_text='2nd!',
        third_text='3rd!',
):
    echo_op(first_text)
    echo_op(second_text)
    echo_op(third_text)


if __name__ == '__main__':
    # Creates <name-of-this-file>.zip that can be uploaded through Kubeflow Pipelines Web UI for usage.
    kfp.compiler.Compiler().compile(echo_chamber_pipeline, __file__ + '.zip')
