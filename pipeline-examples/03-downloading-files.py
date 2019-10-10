import kfp


# What is happening in this script:
# 1. download a file using Google Cloud Storage utility program in the first task (download_op)
# 2. make the contents of the file as output of the first task (download_op)
# 3. use that output as input of the second task (echo_op)
# NB. sometimes containers finish too fast for monitoring so we sleep a bit on each task


def download_as_output_op(url):
    output_file = '/tmp/output.txt'
    return kfp.dsl.ContainerOp(
        name='download',
        image='google/cloud-sdk:216.0.0',
        command=['sh', '-c'],
        arguments=['gsutil cat $0 | tee $1 && sleep 1', url, output_file],
        file_outputs={
            'file-contents': output_file,
        }
    )


def echo_op(text):
    return kfp.dsl.ContainerOp(
        name='echo',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "$0" && sleep 1', text],
    )


@kfp.dsl.pipeline(
    name='Downloading Files - Print Me This File',
    description='Downloads a file and prints its contents.'
)
def download_and_print(
        url='gs://ml-pipeline-playground/shakespeare1.txt',
):
    download_task = download_as_output_op(url)
    echo_op(text=download_task.outputs['file-contents'])


if __name__ == '__main__':
    kfp.compiler.Compiler().compile(download_and_print, __file__ + '.zip')
