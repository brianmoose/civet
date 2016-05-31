import RecipeTester
from ci.tests import utils as test_utils
from ci import models

class RecipeCreatorTests(RecipeTester.RecipeTester):
  def create_default_build_user(self):
    self.server = test_utils.create_git_server(name="github.com")
    self.build_user = test_utils.create_user_with_token(name="moosebuild", server=self.server)

  def create_valid_recipes(self):
    self.create_recipe_in_repo("recipe_all.cfg", "all.cfg")
    self.create_recipe_in_repo("push_dep.cfg", "push_dep.cfg")
    self.create_recipe_in_repo("pr_dep.cfg", "pr_dep.cfg")
    self.create_default_build_user()

  def create_valid_with_check(self):
    # OK. New idaholab/moose/devel
    self.create_valid_recipes()
    self.set_counts()
    self.creator.load_recipes()
    self.compare_counts(recipes=6, sha_changed=True, current=6, users=1, repos=1, branches=1, deps=2, num_push_recipes=2, num_manual_recipes=1, num_pr_recipes=2, num_pr_alt_recipes=1)
  def test_no_recipes(self):
    # no recipes, nothing to do
    self.set_counts()
    self.creator.load_recipes()
    self.compare_counts(sha_changed=True)

  def test_no_user(self):
    # moosebuild user doesn't exist
    self.set_counts()
    self.create_recipe_in_repo("push_dep.cfg", "push_dep.cfg")
    with self.assertRaises(RecipeTester.RecipeRepoReader.InvalidRecipe):
      self.creator.load_recipes()
    self.compare_counts()

  def test_load_ok(self):
    # OK
    self.create_recipe_in_repo("push_dep.cfg", "push_dep.cfg")
    self.create_default_build_user()
    self.set_counts()
    self.creator.load_recipes()
    self.compare_counts(recipes=2, current=2, sha_changed=True, users=1, repos=1, branches=1, num_push_recipes=1, num_pr_alt_recipes=1)

  def test_no_dep(self):
    # dependency file doesn't exist
    self.set_counts()
    self.create_recipe_in_repo("recipe_all.cfg", "all.cfg")
    with self.assertRaises(RecipeTester.RecipeRepoReader.InvalidRecipe):
      self.creator.load_recipes()
    self.compare_counts()

  def test_dep_invalid(self):
    # dependency file isn't valid
    self.set_counts()
    self.create_recipe_in_repo("recipe_all.cfg", "all.cfg")
    self.create_recipe_in_repo("push_dep.cfg", "pr_dep.cfg")
    self.create_recipe_in_repo("pr_dep.cfg", "push_dep.cfg")
    with self.assertRaises(RecipeTester.RecipeRepoReader.InvalidDependency):
      self.creator.load_recipes()
    self.compare_counts()

  def test_load_deps_ok(self):
    # OK. New idaholab/moose/devel
    self.create_valid_with_check()

  def test_no_change(self):
    # Start off with valid recipes
    self.create_valid_with_check()

    # OK, repo sha hasn't changed so no changes.
    self.set_counts()
    self.creator.load_recipes()
    self.compare_counts()

  def test_recipe_changed(self):
    # start with valid recipes
    self.create_valid_with_check()

    # a recipe changed, should have a new recipe but since
    # none of the recipes have jobs attached, the old ones
    # will get deleted and get recreated.
    pr_recipe = self.find_recipe_dict("recipes/pr_dep.cfg")
    pr_recipe["priority_pull_request"] = 100
    self.write_recipe_to_repo(pr_recipe, "pr_dep.cfg")
    self.set_counts()
    self.creator.load_recipes()
    self.compare_counts(sha_changed=True)

  def test_changed_recipe_with_jobs(self):
    # start with valid recipes
    self.create_valid_with_check()

    # change a recipe but now the old ones have jobs attached.
    # so 1 new recipe should be added
    for r in models.Recipe.objects.all():
      test_utils.create_job(recipe=r, user=self.build_user)

    pr_recipe = self.find_recipe_dict("recipes/pr_dep.cfg")
    pr_recipe["priority_pull_request"] = 99
    self.write_recipe_to_repo(pr_recipe, "pr_dep.cfg")
    self.set_counts()
    self.creator.load_recipes()
    self.compare_counts(sha_changed=True, recipes=1, num_pr_recipes=1)
    q = models.Recipe.objects.filter(filename=pr_recipe["filename"])
    self.assertEqual(q.count(), 2)
    q = q.filter(current=True)
    self.assertEqual(q.count(), 1)
    new_r = q.first()
    q = models.Recipe.objects.filter(filename=new_r.filename).exclude(pk=new_r.pk)
    self.assertEqual(q.count(), 1)
    old_r = q.first()
    self.assertNotEqual(old_r.filename_sha, new_r.filename_sha)

  def test_pr_alt_deps(self):
    self.create_default_build_user()
    self.create_recipe_in_repo("push.cfg", "push.cfg")
    self.set_counts()
    # push depends on push_dep.cfg
    # alt_pr depends on pr_dep.cfg
    with self.assertRaises(RecipeTester.RecipeRepoReader.InvalidRecipe):
      self.creator.load_recipes()
    self.compare_counts()

    self.create_recipe_in_repo("push_dep.cfg", "push_dep.cfg")
    self.create_recipe_in_repo("push_dep.cfg", "pr_dep.cfg")
    self.set_counts()
    with self.assertRaises(RecipeTester.RecipeRepoReader.InvalidDependency):
      self.creator.load_recipes()
    self.compare_counts()

    self.create_recipe_in_repo("pr_dep.cfg", "pr_dep.cfg")
    self.creator.load_recipes()
    self.compare_counts(recipes=5, sha_changed=True, current=5, users=1, repos=1, branches=1, deps=2, num_push_recipes=2, num_pr_recipes=1, num_pr_alt_recipes=2)
