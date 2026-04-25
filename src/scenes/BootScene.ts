import * as Phaser from 'phaser';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('BootScene');
  }

  create(): void {
    this.registry.set('gameTitle', '孤屿霜尘');
    this.scene.start('PreloadScene');
  }
}
