import kfp


# What is happening:
# 1. create two tasks where an output of the first task (reverse) is used as an input to the second task (echo).
# NB. sometimes containers finish too fast for monitoring so we sleep a bit on each task

def reverse_as_output_op(text):
    output_file = '/tmp/output.txt'
    return kfp.dsl.ContainerOp(
        name='reverse',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "$0" | rev > $1 && sleep 1', text, output_file],
        file_outputs={
            'reversed-text': output_file,
        }
    )


# NB. in an actual project, you would reuse operations e.g. the echo operation from the 01-simple-tasks example
def echo_op(text):
    return kfp.dsl.ContainerOp(
        name='echo',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "$0" && sleep 1', text],
    )


@kfp.dsl.pipeline(
    name='Output-to-Input Passing - Reverse Echo',
    description='Pass output of the first task as an input to the second task; reverse and print the given text.'
)
def reverse_echo_pipeline(
        text='Hello world!',
):
    reverse_task = reverse_as_output_op(text=text)
    echo_op(text=reverse_task.outputs['reversed-text'])


if __name__ == '__main__':
    kfp.compiler.Compiler().compile(reverse_echo_pipeline, __file__ + '.zip')
