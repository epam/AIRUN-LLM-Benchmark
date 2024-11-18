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

> _**A dataset for testing scenarious was created based on the codebase from the following open-source repositories:**_
> - https://github.com/CosmoCMS/Cosmo
> - https://github.com/danjac/podbaby
> - https://github.com/tastejs/todomvc/tree/master/examples/typescript-react/js
> - https://github.com/tastejs/todomvc/tree/master/examples/typescript-angular/js
> - https://github.com/tastejs/todomvc/tree/master/examples/jquery

## How to Set Up project

### Prepare Python Virtual Environment

1. Create a Python virtual environment
   ```bash
   python -m venv .venv
   ```
2. Activate virtual env using respective Linux or Windows command
   ```bash
   source .venv/bin/activate
   ```
   or
   ```bash
   .venv\Scripts\activate
   ```
3. Install necessary dependencies:
   ```bash
   pip install -r ./requirements.txt
   ```
4. (Optional) Connect your python venv with your IDE

### Environment Variables Setup

Before running the scripts, create a .env file in the root directory of the project using .env.example as a template. Fill in all the necessary environment variables with values specific to your environment.

```bash 
cp .env.example .env
```

## How to complete experiment

### Prepare data

1. Add repos to Dataset. Before adding - create sub directory with the name of language, i.e. "JS"
2. Next in Config folder create json file with the name of your language i.e. "JS" for each LLM you want to launch
3. Then go to Scenarios directory and add Templates to Task_Templates inside LLM you want to launch folder with subdirectory of your language
4. In `Utils/constants.py` add to mapping info about complexity_size of your repositories

### Complete experiment

1. Enrich templates with repos code (files will be created at `/Scenarios/Compiled_Tasks/{model}/{lang}`)
    - Open [run_tasks.ipynb](run_tasks.ipynb) => 1st cell
    - Edit model and lang and start cell
2. Run experiment
    - Edit data for experiment and start cell

## Contributing

We appreciate all contributions to improve the AI/RUN <sup>TM</sup> Engineering Benchmark. Please see
our [Contribution Guidelines](CONTRIBUTING.md) for more information on how to get involved.

If you have suggestions for new benchmark scenarios or improvements to existing ones, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the [Apache 2.0](/LICENSE).

<p align="center">
  EPAM and EPAM AI/RUN <sup>TM</sup> are trademarks of EPAM Systems, Inc. 
</p>

