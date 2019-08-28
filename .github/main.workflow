workflow "New workflow" {
  on = "push"
  resolves = ["Upload artifact"]
}

action "Upload artifact" {
  uses = "actions/upload-artifact@4a2b9e366e87dc28eb136753ae938a81944e431e"
}
