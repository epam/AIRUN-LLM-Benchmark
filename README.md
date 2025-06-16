# LLM Benchmark Framework

## Objective

The objective of this benchmark is to evaluate the performance of the language models in different scenarios. It is a part of AI/RUN <sup>TM</sup> Engineering Benchmark. See more details
in [AI/RUN <sup>TM</sup> Engineering Benchmark repo](https://github.com/epam/AIRUN-Engineering-Benchmark) to understand the whole picture on what the benchmark is and what repositories are involved.

## Evaluation Scenarios

We assess the models using various scenarios such as:

1. Code transformation between different technologies
2. Code generation
3. Documentation generation
4. Large context instructions following

These scenarios allow us to comprehensively evaluate the capabilities and limitations of language models in handling diverse programming tasks and developer interactions.

> _**A dataset for testing scenario was created based on the codebase from the following open-source repositories:**_
> - https://github.com/CosmoCMS/Cosmo
> - https://github.com/danjac/podbaby
> - https://github.com/tastejs/todomvc/tree/master/examples/typescript-react/js
> - https://github.com/tastejs/todomvc/tree/master/examples/typescript-angular/js
> - https://github.com/tastejs/todomvc/tree/master/examples/jquery

## How to Set Up benchmark

### Clone repositories

To complete benchmark, you need to clone the additional repository:

- https://github.com/epam/AIRUN-LLM-Benchmark-Results - for storing results of benchmark

### Prepare Python Virtual Environment

1. Install prerequisites:
- Python (>= 3.12)
- [Poetry](https://python-poetry.org/)

2. Run:
  ```bash
  poetry install
  ```

3. (Optional) Connect your python venv with your IDE

### Environment Variables Setup

Before running the scripts, create a .env file in the root directory of the project using .env.example as a template. Fill in all the necessary environment variables with values specific to your
environment.

```bash 
cp .env.example .env
```

## Prepare for experiment

### Add new model

If you want to add new model to the benchmark, you need to follow these steps:

1. Go to [config.py](Utils/llm/config.py) and add your model to the `Model` class.
2. Use your model in the `run_tasks.ipynb` notebook by selecting it in the Model class.

### Extend dataset

If you want to add new language or repository to the benchmark, you need to follow these steps:

1. Create a new directory in the `Dataset` folder with the name of your language (e.g., "JS" or "Java").
2. Add your repository to the new directory. The repository should contain the code files you want to use in the prompt.
3. Add information about the repository to `Utils/constants.py` file. This includes:
    - `'ToDoApp_ReactJS': 'high_avg'`: means repository "ToDoApp_ReactJS" with **high** complexity and **avg** size.
    - `'ReactSelect': 'React'`: means repository "ReactSelect" with **React** technology.

### Extend categories and scenarios

If you want to add new scenario to the benchmark, you need to follow these steps:

1. Create a new directory `Scenarios/Tasks/{language}` if directory for your language does not exist.
2. Add your category (e.g., "component_test") to the `Scenarios/Tasks/{language}` directory.
3. Add your scenario (e.g., "WriteTestsForComponent_RepoName_complexity_size") to the `Scenarios/Tasks/{language}` directory.
4. Don't forget to add `<place_code_here>` in your scenario file to enrich the template with the code from the repository later.
5. Add criteria to `Scenarios/Tasks/{language}/Criteria` for evaluation results.
6. Launch first cell from [run_tasks.ipynb](run_tasks.ipynb) to enrich the template with the code from the repository.

## How to complete experiment

### Run the benchmark with standard categories

1. Open the [run_tasks.ipynb](run_tasks.ipynb) notebook.
2. Start from the second cell, you can set model and scenarios to run or skip.
3. Next cell generate summary report in AIRUN-LLM-Benchmark-Results repository.
4. Last cell will evaluate the results and generate report in AIRUN-LLM-Benchmark-Results repository.
5. Result will be in `AIRUN-LLM-Benchmark-Results` repository in `Output/{model}/{language}` directory.

### Run LCIF experiment

1. Open the [run_contextual_task.ipynb](run_contextual_task.ipynb)
2. Change model to use in the experiment
3. Start all cells
4. Result will be in `AIRUN-LLM-Benchmark-Results` repository in `Output/{model}/{language}/contextual_experiment` directory.

## Contributing

We appreciate all contributions to improve the AI/RUN <sup>TM</sup> Engineering Benchmark. Please see
our [Contribution Guidelines](CONTRIBUTING.md) for more information on how to get involved.

If you have suggestions for new benchmark scenarios or improvements to existing ones, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the [Apache 2.0](/LICENSE).

<p align="center">
  EPAM and EPAM AI/RUN <sup>TM</sup> are trademarks of EPAM Systems, Inc. 
</p>

